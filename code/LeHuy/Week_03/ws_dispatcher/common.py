import json
import os
import time
from decimal import Decimal
from datetime import datetime, timezone

import boto3


# Các bảng được cấu hình qua biến môi trường.
db = boto3.resource("dynamodb", region_name="us-east-1")

orders = db.Table(os.environ["ORDERS_TABLE"])
connections = db.Table(os.environ["CONNECTIONS_TABLE"])
tasks = db.Table(os.environ["TASKS_TABLE"])


class APIError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def decimal_to_json(value):
    """Chuyển Number của DynamoDB thành số JSON."""
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)

    raise TypeError(
        f"Unsupported JSON type: {type(value).__name__}"
    )


def read(table, key):
    """Đọc dữ liệu mới nhất từ bảng chính."""
    response = table.get_item(
        Key=key,
        ConsistentRead=True
    )
    return response.get("Item")


def can_read(actor, order):
    """Kiểm tra quyền xem đơn theo danh tính do backend quản lý."""
    if actor.get("role") == "CUSTOMER":
        return order.get("customerId") == actor.get("id")

    if actor.get("role") == "DRIVER":
        return (
            order.get("status") == "PLACED"
            or order.get("driverId") == actor.get("id")
        )

    return False


def snapshot(order):
    """Chỉ lấy các trường cần gửi về giao diện."""
    return {
        "orderId": order["orderId"],
        "status": order["status"],
        "workflowStatus": order.get("workflowStatus"),
        "version": int(order["version"]),
        "updatedAt": order.get("updatedAt"),
        "driverId": order.get("driverId")
    }


def load_order(oid, actor):
    """Đọc đơn và kiểm tra quyền truy cập."""
    if not isinstance(oid, str) or not oid.strip():
        raise APIError("VALIDATION_ERROR")

    order = read(
        orders,
        {"orderId": oid}
    )

    if not order:
        raise APIError("NOT_FOUND")

    if not can_read(actor, order):
        raise APIError("FORBIDDEN")

    return order


def actor_for_connection(cid):
    """Lấy danh tính từ bản ghi kết nối đã được backend tạo."""
    item = read(
        connections,
        {"connectionId": cid}
    )

    if not item:
        raise APIError("UNAUTHORIZED")

    try:
        expires_at = int(item.get("expiresAt", 0))
    except (TypeError, ValueError, OverflowError):
        raise APIError("UNAUTHORIZED")

    if expires_at <= time.time():
        raise APIError("UNAUTHORIZED")

    actor_id = item.get("actorId")
    role = item.get("role")

    if (
        not isinstance(actor_id, str)
        or not actor_id
        or role not in ("CUSTOMER", "DRIVER")
    ):
        raise APIError("UNAUTHORIZED")

    return {
        "id": actor_id,
        "role": role
    }


def manager(endpoint):
    """Tạo client gửi tin về kết nối WebSocket."""
    return boto3.client(
        "apigatewaymanagementapi",
        region_name="us-east-1",
        endpoint_url=endpoint.rstrip("/")
    )


def send(client, cid, payload):
    """Gửi JSON và dọn bản ghi nếu kết nối không còn tồn tại."""
    try:
        data = json.dumps(
            payload,
            default=decimal_to_json,
            ensure_ascii=False
        ).encode("utf-8")

        client.post_to_connection(
            ConnectionId=cid,
            Data=data
        )
        return True

    except client.exceptions.GoneException:
        connections.delete_item(
            Key={"connectionId": cid}
        )
        return False


def utc():
    """Thời gian UTC dạng ISO 8601."""
    return datetime.now(timezone.utc).isoformat()