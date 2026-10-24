import json
import os
import re
import time

from common import (
    APIError,
    connections,
    actor_for_connection,
    manager,
    send,
    utc,
)
from orders_api import handle_action


ACTIONS = {
    "ping",
    "createOrder",
    "getOrder",
    "subscribeOrder",
    "listOrders",
    "updateOrderStatus",
}


def safe_identifier(value):
    """Chỉ ghi định danh ngắn, không ghi dữ liệu tự do."""
    if (
        isinstance(value, str)
        and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value)
    ):
        return value

    return None


def safe_connection_id(value):
    """Giữ connection ID để truy vết, loại ký tự điều khiển."""
    if (
        isinstance(value, str)
        and 1 <= len(value) <= 256
        and all(33 <= ord(char) <= 126 for char in value)
    ):
        return value

    return None


def safe_order_id(value):
    """Mã đơn ứng dụng tạo: ORD- và 24 ký tự hex."""
    if (
        isinstance(value, str)
        and re.fullmatch(r"ORD-[a-f0-9]{24}", value)
    ):
        return value

    return None


def aws_error_code(exc):
    """Lấy mã lỗi AWS, không ghi toàn bộ nội dung exception."""
    response = getattr(exc, "response", {})

    if not isinstance(response, dict):
        return "UNKNOWN"

    error = response.get("Error", {})

    if not isinstance(error, dict):
        return "UNKNOWN"

    return safe_identifier(error.get("Code")) or "UNKNOWN"


def lambda_handler(event, context):
    started = time.monotonic()

    rc = event.get("requestContext") or {}
    route = rc.get("routeKey")
    cid = rc.get("connectionId")

    trace = {
        "event": "ws_dispatch",
        "lambdaRequestId": getattr(
            context,
            "aws_request_id",
            None,
        ),
        "connectionId": safe_connection_id(cid),
        "route": (
            route
            if route in {"$connect", "$disconnect", "$default"}
            else "CUSTOM_ROUTE"
        ),
    }

    def audit(outcome, code, **extra):
        record = {
            **trace,
            **extra,
            "outcome": outcome,
            "code": safe_identifier(code) or "UNKNOWN",
            "durationMs": round(
                (time.monotonic() - started) * 1000,
                2,
            ),
        }

        # Không ghi toàn bộ event, token, địa chỉ hoặc taskToken.
        print(json.dumps(record, ensure_ascii=False))

    if not route or not cid:
        audit("ERROR", "MISSING_REQUEST_CONTEXT")

        return {
            "statusCode": 400,
            "body": "Missing requestContext",
        }

    # ==================== Ngắt kết nối ====================

    if route == "$disconnect":
        connections.delete_item(
            Key={"connectionId": cid}
        )

        audit("SUCCESS", "DISCONNECTED")

        return {
            "statusCode": 200,
            "body": "Disconnected",
        }

    # ==================== Mở kết nối ====================

    if route == "$connect":
        token = (
            event.get("queryStringParameters") or {}
        ).get("token", "")

        sessions = json.loads(
            os.environ.get("SESSION_TOKENS_JSON", "{}")
        )

        actor = sessions.get(token) if token else None

        if (
            not isinstance(actor, dict)
            or not isinstance(actor.get("id"), str)
            or not actor["id"]
            or actor.get("role") not in ("CUSTOMER", "DRIVER")
        ):
            audit("ERROR", "INVALID_SESSION")

            return {
                "statusCode": 403,
                "body": "Invalid demo session",
            }

        connections.put_item(
            Item={
                "connectionId": cid,
                "actorId": actor["id"],
                "role": actor["role"],
                "connectedAt": utc(),
                "expiresAt": int(time.time()) + 3600,
            }
        )

        audit(
            "SUCCESS",
            "CONNECTED",
            actorId=safe_identifier(actor["id"]),
            role=actor["role"],
        )

        return {
            "statusCode": 200,
            "body": "Connected",
        }

    # ==================== Xử lý yêu cầu ====================

    request_id = None

    try:
        body = json.loads(event.get("body") or "{}")

        if not isinstance(body, dict):
            raise APIError("VALIDATION_ERROR")

        request_id = body.get("requestId")

        if (
            not isinstance(request_id, str)
            or not 1 <= len(request_id) <= 128
        ):
            request_id = None
            raise APIError("VALIDATION_ERROR")

        action = body.get("action")

        trace["action"] = (
            action
            if isinstance(action, str) and action in ACTIONS
            else "UNKNOWN"
        )

        trace["requestId"] = safe_identifier(request_id)
        trace["orderId"] = safe_order_id(body.get("orderId"))

        # Danh tính lấy từ bản ghi kết nối do backend tạo.
        actor = actor_for_connection(cid)

        trace["actorId"] = safe_identifier(actor["id"])
        trace["role"] = actor["role"]

        data = handle_action(body, actor, cid)

        if isinstance(data, dict):
            returned_id = safe_order_id(data.get("orderId"))

            if returned_id:
                trace["orderId"] = returned_id

        result = {
            "type": "RESPONSE",
            "requestId": request_id,
            "ok": True,
            "data": data,
        }

    except (ValueError, TypeError):
        result = {
            "type": "RESPONSE",
            "requestId": request_id,
            "ok": False,
            "error": {
                "code": "VALIDATION_ERROR",
            },
        }

    except APIError as exc:
        result = {
            "type": "RESPONSE",
            "requestId": request_id,
            "ok": False,
            "error": {
                "code": exc.code,
            },
        }

    except Exception as exc:
        trace["exceptionType"] = type(exc).__name__
        trace["awsErrorCode"] = aws_error_code(exc)

        result = {
            "type": "RESPONSE",
            "requestId": request_id,
            "ok": False,
            "error": {
                "code": "INTERNAL_ERROR",
            },
        }

    # ==================== Gửi phản hồi ====================

    result_code = (
        "OK"
        if result["ok"]
        else result["error"]["code"]
    )

    try:
        client = manager(
            "https://" + rc["domainName"] + "/" + rc["stage"]
        )

        delivered = send(client, cid, result)

    except Exception as exc:
        audit(
            "ERROR",
            "RESPONSE_SEND_FAILED",
            resultCode=safe_identifier(result_code),
            exceptionType=type(exc).__name__,
            awsErrorCode=aws_error_code(exc),
        )

        raise

    audit(
        "SUCCESS" if result["ok"] else "ERROR",
        result_code,
        delivered=bool(delivered),
    )

    return {
        "statusCode": 200,
        "body": "Processed",
    }