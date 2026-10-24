import os
import json
import time

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
sfn_client = boto3.client("stepfunctions", region_name=REGION)

TASKS_TABLE = os.environ.get(
    "WORKFLOW_TASKS_TABLE",
    "fooddelivery-workflow-tasks"
)
ORDERS_TABLE = os.environ.get(
    "ORDERS_TABLE",
    "fooddelivery-orders"
)

tasks_table = dynamodb.Table(TASKS_TABLE)
orders_table = dynamodb.Table(ORDERS_TABLE)

VALID_STATUSES = {"ACCEPTED", "DELIVERING", "COMPLETED"}
PREVIOUS_STATUS = {
    "ACCEPTED": "PLACED",
    "DELIVERING": "ACCEPTED",
    "COMPLETED": "DELIVERING"
}


def error_response(code, message):
    return {
        "ok": False,
        "errorCode": code,
        "message": message
    }


def lambda_handler(event, context):
    if not isinstance(event, dict):
        return error_response(
            "VALIDATION_ERROR",
            "Event must be a JSON object."
        )

    order_id = event.get("orderId")
    target_status = event.get("targetStatus")
    actor_id = event.get("actorId")
    request_id = event.get("requestId")
    expected_version = event.get("expectedVersion")

    required_values = [
        order_id,
        target_status,
        actor_id,
        request_id
    ]

    if any(
        not isinstance(value, str) or not value.strip()
        for value in required_values
    ):
        return error_response(
            "VALIDATION_ERROR",
            "orderId, targetStatus, actorId and requestId are required."
        )

    if target_status not in VALID_STATUSES:
        return error_response(
            "VALIDATION_ERROR",
            "targetStatus must be ACCEPTED, DELIVERING or COMPLETED."
        )

    if expected_version is not None:
        if isinstance(expected_version, bool) or not isinstance(expected_version, int) or expected_version < 1:
            return error_response(
                "VALIDATION_ERROR",
                "expectedVersion must be a positive integer."
            )

    key = {
        "orderId": order_id,
        "step": target_status
    }

    # Structured JSON log (TUYỆT ĐỐI KHÔNG IN taskToken)
    print(json.dumps({
        "operation": "submit_transition",
        "orderId": order_id,
        "targetStatus": target_status,
        "actorId": actor_id,
        "requestId": request_id,
        "expectedVersion": expected_version
    }))

    # 1. Đọc bước chờ hiện tại trong WorkflowTasks
    try:
        response = tasks_table.get_item(
            Key=key,
            ConsistentRead=True
        )
    except ClientError as exc:
        print("Read task failed:", exc.response["Error"]["Code"])
        return error_response(
            "READ_TASK_FAILED",
            "Cannot read the workflow task."
        )

    task = response.get("Item")

    if not task:
        return error_response(
            "NOT_READY",
            "The workflow has not prepared this step yet."
        )

    task_state = task.get("taskState")

    same_request = (
        task.get("requestId") == request_id
        and task.get("actorId") == actor_id
    )

    # 2. Xử lý Idempotency: Nhận diện yêu cầu đã xử lý hoặc đang xử lý
    if task_state == "DONE":
        if same_request:
            return {
                "ok": True,
                "status": "ALREADY_DONE",
                "orderId": order_id,
                "step": target_status
            }

        return error_response(
            "CONFLICT",
            "This step has already been completed by another request."
        )

    if task_state == "CLAIMED":
        if same_request:
            return {
                "ok": True,
                "status": "PROCESSING",
                "orderId": order_id,
                "step": target_status,
                "message": (
                    "The request was claimed. Check the workflow "
                    "and Orders to confirm the result."
                )
            }

        return error_response(
            "CONFLICT",
            "This step is already claimed by another request."
        )

    if task_state != "READY":
        return error_response(
            "NOT_READY",
            "This task is not in READY state."
        )

    task_token = task.get("taskToken")
    expires_at = task.get("expiresAt")
    now = int(time.time())

    if not isinstance(task_token, str) or not task_token:
        return error_response(
            "INVALID_TASK",
            "The task has no valid callback token."
        )

    try:
        expired = (
            expires_at is None
            or int(expires_at) <= now
        )
    except (TypeError, ValueError, OverflowError):
        return error_response(
            "INVALID_TASK",
            "The task expiry value is invalid."
        )

    if expired:
        return error_response(
            "TASK_EXPIRED",
            "The task record has expired. Check the execution."
        )

    # 3. Đọc và kiểm tra Orders (nghiệp vụ & quyền)
    try:
        order_resp = orders_table.get_item(
            Key={"orderId": order_id},
            ConsistentRead=True
        )
        order = order_resp.get("Item")
        if order:
            # Kiểm tra trạng thái trước hợp lệ
            expected_prev = PREVIOUS_STATUS[target_status]
            if order.get("status") != expected_prev:
                return error_response(
                    "CONFLICT",
                    f"Order status {order.get('status')} does not match required previous status {expected_prev}."
                )
            # Kiểm tra quyền tài xế cho các bước sau nhận đơn
            if target_status in ("DELIVERING", "COMPLETED") and order.get("driverId") != actor_id:
                return error_response(
                    "FORBIDDEN",
                    "Only the assigned driver can update this order."
                )
            # Kiểm tra Optimistic Concurrency Control nếu client truyền expectedVersion
            if expected_version is not None and order.get("version") != expected_version:
                return error_response(
                    "CONFLICT",
                    f"Version mismatch: expected {expected_version}, current is {order.get('version')}."
                )
    except ClientError as exc:
        print("Read order check warning:", exc.response["Error"]["Code"])

    # 4. Atomic claim: Chỉ duy nhất 1 yêu cầu chuyển READY sang CLAIMED
    try:
        tasks_table.update_item(
            Key=key,
            UpdateExpression=(
                "SET taskState = :claimed, "
                "actorId = :actor, "
                "requestId = :request, "
                "claimedAt = :now"
            ),
            ConditionExpression=(
                "taskState = :ready "
                "AND taskToken = :token "
                "AND expiresAt > :now"
            ),
            ExpressionAttributeValues={
                ":claimed": "CLAIMED",
                ":ready": "READY",
                ":actor": actor_id,
                ":request": request_id,
                ":now": now,
                ":token": task_token
            }
        )
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        print("Claim task failed:", code)

        if code == "ConditionalCheckFailedException":
            return error_response(
                "CONFLICT",
                "The task changed, expired or was claimed by another request."
            )

        return error_response(
            "CLAIM_FAILED",
            "Cannot claim the workflow task."
        )

    # 5. Output callback truyền cho Step Functions (khớp $.transitionResult trong ASL)
    callback_output = {
        "orderId": order_id,
        "step": target_status,
        "actorId": actor_id,
        "requestId": request_id
    }

    try:
        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(callback_output)
        )

    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        print("SendTaskSuccess failed:", code)

        # Khi bị từ chối quyền rõ ràng, trả claim về READY
        if code in {
            "AccessDenied",
            "AccessDeniedException",
            "UnauthorizedException"
        }:
            try:
                tasks_table.update_item(
                    Key=key,
                    UpdateExpression=(
                        "SET taskState = :ready "
                        "REMOVE actorId, requestId, claimedAt"
                    ),
                    ConditionExpression=(
                        "taskState = :claimed "
                        "AND actorId = :actor "
                        "AND requestId = :request "
                        "AND taskToken = :token"
                    ),
                    ExpressionAttributeValues={
                        ":ready": "READY",
                        ":claimed": "CLAIMED",
                        ":actor": actor_id,
                        ":request": request_id,
                        ":token": task_token
                    }
                )
            except ClientError as release_error:
                print(
                    "Release claim failed:",
                    release_error.response["Error"]["Code"]
                )

            return error_response(
                "CALLBACK_DENIED",
                "Callback permission was denied. Check LabRole permissions."
            )

        if code in {
            "TaskTimedOut",
            "TaskDoesNotExist",
            "InvalidToken"
        }:
            return error_response(
                "CALLBACK_INVALID",
                "The callback token is no longer usable. Check the execution."
            )

        # Chưa chắc callback đã được nhận hay chưa: giữ claim để đối chiếu
        return error_response(
            "CALLBACK_UNCERTAIN",
            "Check the execution and Orders before retrying."
        )

    except Exception as exc:
        print("Callback transport error:", type(exc).__name__)
        return error_response(
            "CALLBACK_UNCERTAIN",
            "The callback result is uncertain. Check the execution and Orders."
        )

    return {
        "ok": True,
        "status": "QUEUED",
        "orderId": order_id,
        "step": target_status,
        "message": (
            "Callback sent. Check Orders to confirm the committed state."
        )
    }
