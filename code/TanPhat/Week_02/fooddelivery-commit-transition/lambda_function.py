
import os
import json
import time
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError


REGION = "us-east-1"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
ddb_client = boto3.client("dynamodb", region_name=REGION)
sns_client = boto3.client("sns", region_name=REGION)

ORDERS_TABLE = os.environ.get(
    "ORDERS_TABLE",
    "fooddelivery-orders"
)

TASKS_TABLE = os.environ.get(
    "WORKFLOW_TASKS_TABLE",
    "fooddelivery-workflow-tasks"
)

SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

orders_table = dynamodb.Table(ORDERS_TABLE)
tasks_table = dynamodb.Table(TASKS_TABLE)

serializer = TypeSerializer()

PREVIOUS_STATUS = {
    "ACCEPTED": "PLACED",
    "DELIVERING": "ACCEPTED",
    "COMPLETED": "DELIVERING"
}


def serialize_map(values):
    return {
        key: serializer.serialize(value)
        for key, value in values.items()
    }


def is_same_completed_task(task, actor_id, request_id):
    return (
        task is not None
        and task.get("taskState") == "DONE"
        and task.get("actorId") == actor_id
        and task.get("requestId") == request_id
    )


def duplicate_result(order_id, step, task):
    saved_version = task.get("committedVersion")

    return {
        "ok": True,
        "orderId": order_id,
        "step": step,
        "status": "COMMITTED",
        "duplicate": True,
        "version": (
            int(saved_version)
            if saved_version is not None
            else None
        ),
        "sns": "SKIPPED_DUPLICATE"
    }


def lambda_handler(event, context):
    # 1. Kiểm tra đầu vào trước khi truy cập dữ liệu.
    if not isinstance(event, dict):
        raise ValueError("Event must be a JSON object.")

    order_id = event.get("orderId")
    step = event.get("step")
    actor_id = event.get("actorId")
    request_id = event.get("requestId")

    required = [
        order_id,
        step,
        actor_id,
        request_id
    ]

    if any(
        not isinstance(value, str) or not value.strip()
        for value in required
    ):
        raise ValueError(
            "Missing or invalid orderId, step, actorId or requestId."
        )

    if step not in PREVIOUS_STATUS:
        raise ValueError(
            "step must be ACCEPTED, DELIVERING or COMPLETED."
        )

    # Không log toàn bộ event hoặc taskToken.
    print(json.dumps({
        "operation": "commit_transition",
        "orderId": order_id,
        "step": step,
        "actorId": actor_id,
        "requestId": request_id
    }))

    task_key = {
        "orderId": order_id,
        "step": step
    }

    # 2. Kiểm tra bước đã được submit claim.
    task = tasks_table.get_item(
        Key=task_key,
        ConsistentRead=True
    ).get("Item")

    if is_same_completed_task(task, actor_id, request_id):
        return duplicate_result(order_id, step, task)

    if not task:
        raise ValueError("Workflow task does not exist.")

    if (
        task.get("taskState") != "CLAIMED"
        or task.get("actorId") != actor_id
        or task.get("requestId") != request_id
    ):
        raise ValueError(
            "Task is not CLAIMED by this actor and request."
        )

    # 3. Đọc và kiểm tra đơn trước khi chuyển trạng thái.
    order = orders_table.get_item(
        Key={"orderId": order_id},
        ConsistentRead=True
    ).get("Item")

    if not order:
        raise ValueError("Order does not exist.")

    previous_status = PREVIOUS_STATUS[step]

    if order.get("status") != previous_status:
        raise ValueError(
            "Order status does not match the required previous status."
        )

    current_version = order.get("version")

    if (
        isinstance(current_version, bool)
        or not isinstance(current_version, (int, Decimal))
        or current_version < 1
        or current_version != int(current_version)
    ):
        raise ValueError(
            "Order version must be a positive integer Number."
        )

    current_version = int(current_version)
    next_version = current_version + 1

    if step != "ACCEPTED" and order.get("driverId") != actor_id:
        raise ValueError(
            "Only the assigned driver can update this order."
        )

    now = int(time.time())

    workflow_status = (
        "SUCCEEDED" if step == "COMPLETED" else "RUNNING"
    )

    # 4. Chuẩn bị cập nhật Orders có điều kiện.
    order_update = (
        "SET #status = :next, "
        "#version = :new_version, "
        "updatedAt = :now, "
        "lastTransitionRequestId = :request, "
        "workflowStatus = :workflow"
    )

    order_condition = (
        "#status = :previous AND #version = :old_version"
    )

    if step == "ACCEPTED":
        order_update += ", driverId = :actor"
    else:
        order_condition += " AND driverId = :actor"

    order_values = {
        ":next": step,
        ":previous": previous_status,
        ":old_version": current_version,
        ":new_version": next_version,
        ":now": now,
        ":request": request_id,
        ":workflow": workflow_status,
        ":actor": actor_id
    }

    # Orders và WorkflowTasks phải cùng được cập nhật.
    try:
        ddb_client.transact_write_items(
            TransactItems=[
                {
                    "Update": {
                        "TableName": ORDERS_TABLE,
                        "Key": serialize_map({
                            "orderId": order_id
                        }),
                        "UpdateExpression": order_update,
                        "ConditionExpression": order_condition,
                        "ExpressionAttributeNames": {
                            "#status": "status",
                            "#version": "version"
                        },
                        "ExpressionAttributeValues": serialize_map(
                            order_values
                        )
                    }
                },
                {
                    "Update": {
                        "TableName": TASKS_TABLE,
                        "Key": serialize_map(task_key),
                        "UpdateExpression": (
                            "SET taskState = :done, "
                            "committedAt = :now, "
                            "committedVersion = :new_version "
                            "REMOVE taskToken"
                        ),
                        "ConditionExpression": (
                            "taskState = :claimed "
                            "AND actorId = :actor "
                            "AND requestId = :request"
                        ),
                        "ExpressionAttributeValues": serialize_map({
                            ":done": "DONE",
                            ":claimed": "CLAIMED",
                            ":now": now,
                            ":new_version": next_version,
                            ":actor": actor_id,
                            ":request": request_id
                        })
                    }
                }
            ]
        )

    except ClientError as exc:
        error_code = exc.response["Error"]["Code"]
        print("Commit transaction failed:", error_code)

        # Một lần gọi song song có thể vừa commit cùng yêu cầu.
        if error_code == "TransactionCanceledException":
            latest_task = tasks_table.get_item(
                Key=task_key,
                ConsistentRead=True
            ).get("Item")

            if is_same_completed_task(
                latest_task,
                actor_id,
                request_id
            ):
                return duplicate_result(
                    order_id,
                    step,
                    latest_task
                )

        # Ném lỗi để workflow biết commit chưa thành công.
        raise

    print(
        f"Committed order={order_id}, "
        f"step={step}, version={next_version}"
    )

    # 5. SNS được gửi sau khi dữ liệu đã commit.
    sns_status = "NOT_REQUIRED"

    if step in {"ACCEPTED", "COMPLETED"}:
        if not SNS_TOPIC_ARN:
            sns_status = "NOT_CONFIGURED"
        else:
            message = {
                "orderId": order_id,
                "status": step,
                "version": next_version,
                "actorId": actor_id,
                "timestamp": now
            }

            try:
                sns_client.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject=f"FoodDelivery: Order is now {step}",
                    Message=json.dumps(message)
                )

                sns_status = "PUBLISHED"

            except Exception as exc:
                # Không rollback đơn đã commit vì lỗi thông báo.
                if isinstance(exc, ClientError):
                    code = exc.response["Error"]["Code"]
                else:
                    code = type(exc).__name__

                print("SNS publish failed:", code)
                sns_status = "FAILED"

    return {
        "ok": True,
        "orderId": order_id,
        "step": step,
        "status": "COMMITTED",
        "version": next_version,
        "duplicate": False,
        "sns": sns_status
    }
