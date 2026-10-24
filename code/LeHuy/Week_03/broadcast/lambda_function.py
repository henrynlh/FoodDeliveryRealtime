import json
import os
import re
import time

from boto3.dynamodb.conditions import Key

from common import (
    orders,
    connections,
    read,
    can_read,
    snapshot,
    manager,
    send,
)


def safe_order_id(value):
    """Chỉ ghi mã đơn đúng định dạng vào log."""
    if (
        isinstance(value, str)
        and re.fullmatch(r"ORD-[a-f0-9]{24}", value)
    ):
        return value

    return None


def safe_error_code(exc):
    """Không ghi toàn bộ exception vì có thể chứa dữ liệu nhạy cảm."""
    response = getattr(exc, "response", {})

    if isinstance(response, dict):
        error = response.get("Error", {})

        if isinstance(error, dict):
            code = error.get("Code")

            if (
                isinstance(code, str)
                and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", code)
            ):
                return code

    return "UNKNOWN"


def valid_subscription(current, oid, order):
    """Kiểm tra lại bản ghi chính sau khi đọc kết quả từ GSI."""
    if not current or current.get("orderId") != oid:
        return False

    try:
        expires_at = int(current.get("expiresAt", 0))
    except (TypeError, ValueError, OverflowError):
        return False

    if expires_at <= time.time():
        return False

    actor_id = current.get("actorId")
    role = current.get("role")

    if (
        not isinstance(actor_id, str)
        or not actor_id
        or role not in ("CUSTOMER", "DRIVER")
    ):
        return False

    return can_read(
        {
            "id": actor_id,
            "role": role,
        },
        order,
    )


def lambda_handler(event, context):
    started = time.monotonic()

    trace = {
        "event": "ws_broadcast",
        "lambdaRequestId": getattr(
            context,
            "aws_request_id",
            None,
        ),
    }

    sent = 0
    skipped = 0
    gone = 0

    def audit(outcome, code, **extra):
        record = {
            **trace,
            **extra,
            "outcome": outcome,
            "code": code,
            "sent": sent,
            "skipped": skipped,
            "gone": gone,
            "durationMs": round(
                (time.monotonic() - started) * 1000,
                2,
            ),
        }

        # Không ghi event đầy đủ, token, địa chỉ hoặc taskToken.
        print(json.dumps(record, ensure_ascii=False))

    if not isinstance(event, dict):
        audit("ERROR", "VALIDATION_ERROR")

        return {
            "ok": False,
            "error": "VALIDATION_ERROR",
        }

    oid = event.get("orderId")

    if not isinstance(oid, str) or not oid.strip():
        audit("ERROR", "VALIDATION_ERROR")

        return {
            "ok": False,
            "error": "VALIDATION_ERROR",
        }

    trace["orderId"] = safe_order_id(oid)

    try:
        order = read(
            orders,
            {"orderId": oid},
        )

        if not order:
            audit("ERROR", "NOT_FOUND")

            return {
                "ok": False,
                "error": "NOT_FOUND",
            }

        order_snapshot = snapshot(order)

        trace["status"] = order_snapshot["status"]
        trace["version"] = order_snapshot["version"]

        payload = {
            "type": "ORDER_UPDATED",
            **order_snapshot,
        }

        client = manager(
            os.environ["WS_ENDPOINT_URL"].rstrip("/")
        )

        args = {
            "IndexName": "ByOrderId",
            "KeyConditionExpression": Key("orderId").eq(oid),
        }

        while True:
            page = connections.query(**args)

            for row in page.get("Items", []):
                cid = row.get("connectionId")

                if not isinstance(cid, str) or not cid:
                    skipped += 1
                    continue

                # GSI có thể trả dữ liệu cũ:
                # đọc lại bản ghi chính để kiểm tra đăng ký và quyền.
                current = read(
                    connections,
                    {"connectionId": cid},
                )

                if not valid_subscription(current, oid, order):
                    skipped += 1
                    continue

                if send(client, cid, payload):
                    sent += 1
                else:
                    # common.send xử lý GoneException và xóa kết nối.
                    gone += 1

            cursor = page.get("LastEvaluatedKey")

            if not cursor:
                break

            args["ExclusiveStartKey"] = cursor

        audit("SUCCESS", "BROADCAST_FINISHED")

        return {
            "ok": True,
            "sent": sent,
            "skipped": skipped,
            "gone": gone,
        }

    except Exception as exc:
        audit(
            "ERROR",
            "BROADCAST_FAILED",
            exceptionType=type(exc).__name__,
            awsErrorCode=safe_error_code(exc),
        )

        # Giữ cơ chế báo lỗi cho workflow đang gọi Lambda.
        raise