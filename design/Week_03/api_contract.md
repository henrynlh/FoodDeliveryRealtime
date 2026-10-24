# HỢP ĐỒNG GIAO TIẾP DỮ LIỆU & API – TUẦN 3 (API CONTRACT)

- **Hệ thống:** FoodDeliveryRealtime
- **Phụ trách soạn thảo:** Trương Tấn Phát (TV1)
- **Phụ trách đối chiếu:** Nguyễn Lê Huy (TV2)
- **Ngày thống nhất:** 24/10/2026
- **Trạng thái:** Đã thống nhất cho tích hợp tuần 3

---

## 1. Bảng quy chuẩn chuyển dịch trạng thái & Versioning

| Bước nghiệp vụ (`step`) | Trạng thái trước | Trạng thái sau (`targetStatus`) | Version trước | Version sau khi Commit | Người thực hiện (`actorId`) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Khởi tạo đơn** | *(Chưa có)* | `PLACED` | 0 | 1 | Khách hàng |
| **Nhận đơn** | `PLACED` | `ACCEPTED` | 1 | 2 | Tài xế nhận đơn |
| **Bắt đầu giao** | `ACCEPTED` | `DELIVERING` | 2 | 3 | Tài xế phụ trách đơn |
| **Hoàn tất giao** | `DELIVERING` | `COMPLETED` | 3 | 4 | Tài xế phụ trách đơn |

---

## 2. Giao thức yêu cầu chuyển trạng thái (Client -> Dispatcher -> Submit Lambda)

### 2.1. Client WebSocket gửi lên API Gateway:
```json
{
  "action": "updateOrderStatus",
  "orderId": "ORD-20261024-001",
  "targetStatus": "ACCEPTED",
  "expectedVersion": 1,
  "requestId": "W3-REQ-uuid-v4-001"
}
```
*Lưu ý:* `actorId` không gửi từ trình duyệt mà do `ws_dispatcher` tự động xác thực và trích xuất từ connection context (`C001`, `D001`, `D002`).

### 2.2. Dispatcher chuyển tiếp tới Lambda `submit-transition`:
```json
{
  "orderId": "ORD-20261024-001",
  "targetStatus": "ACCEPTED",
  "actorId": "D001",
  "requestId": "W3-REQ-uuid-v4-001",
  "expectedVersion": 1
}
```

---

## 3. Quy chuẩn phản hồi từ Backend (Response Contract)

### 3.1. Phản hồi thành công từ Submit Lambda:
1. **Lần đầu tiếp nhận callback thành công (Chờ Step Functions commit):**
   ```json
   {
     "ok": true,
     "status": "QUEUED",
     "orderId": "ORD-20261024-001",
     "step": "ACCEPTED",
     "message": "Callback sent. Check Orders to confirm the committed state."
   }
   ```
2. **Yêu cầu đang được xử lý (trùng requestId khi task đang CLAIMED):**
   ```json
   {
     "ok": true,
     "status": "PROCESSING",
     "orderId": "ORD-20261024-001",
     "step": "ACCEPTED"
   }
   ```
3. **Yêu cầu đã hoàn tất trước đó (Idempotency - gửi lại cùng requestId khi task đã DONE):**
   ```json
   {
     "ok": true,
     "status": "ALREADY_DONE",
     "orderId": "ORD-20261024-001",
     "step": "ACCEPTED"
   }
   ```

### 3.2. Phản hồi lỗi (Error Response):
```json
{
  "ok": false,
  "errorCode": "CONFLICT",
  "message": "This step is already claimed by another request."
}
```

### 3.3. Danh mục mã lỗi chuẩn (`errorCode`):
- `VALIDATION_ERROR`: Thiếu trường bắt buộc (`orderId`, `targetStatus`, `actorId`, `requestId`) hoặc sai định dạng dữ liệu.
- `NOT_READY`: Bước chờ trong State Machine chưa được khởi tạo ở trạng thái `READY`.
- `CONFLICT`: 
  - Bước đã bị tài xế khác claim trước trong bảng `WorkflowTasks`.
  - Hoặc `expectedVersion` gửi lên không khớp với phiên bản hiện tại của đơn hàng trong `Orders`.
- `VERSION_MISMATCH`: Phiên bản dữ liệu client gửi lên cũ hơn phiên bản thực tế trên hệ thống.
- `FORBIDDEN`: Tài xế không được phân công cố tình chuyển trạng thái đơn hàng.
- `TASK_EXPIRED`: Bản ghi bước chờ trong DynamoDB đã quá hạn thời gian xử lý.
- `CALLBACK_INVALID`: Task token của Step Functions đã hết hạn hoặc không tồn tại (quá 300 giây).
- `CALLBACK_DENIED`: Bị Step Functions từ chối quyền gọi `SendTaskSuccess` do LabRole.

---

## 4. Chính sách phát lại thông báo (Notification & Duplicate Policy)

1. **Commit Idempotency:** Khi Lambda `commit-transition` phát hiện `lastRequestId == requestId` hoặc task đã ở trạng thái `DONE`:
   - Không tăng `version` của đơn hàng.
   - Trả về `"duplicate": true`, `"sns": "SKIPPED_DUPLICATE"`.
   - Không gửi thêm thông báo SNS trùng lặp.
2. **Chính sách Realtime Broadcast:** Khi commit thành công, trạng thái mới nhất (`ORDER_UPDATED`) sẽ được Lambda `broadcast` phát tới các WebSocket client đang theo dõi đơn hàng.
