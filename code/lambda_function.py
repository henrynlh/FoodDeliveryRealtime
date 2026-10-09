import json
import os
import time
from datetime import datetime, timezone
import boto3

TABLE = os.environ["CONNECTIONS_TABLE"]
table = boto3.resource("dynamodb").Table(TABLE)

def lambda_handler(event, context):
    rc = event.get("requestContext", {})
    route = rc.get("routeKey")
    cid = rc.get("connectionId")
    if not route or not cid:
        return {"statusCode": 400, "body": "Missing context"}
    if route == "$connect":
        table.put_item(Item={
            "connectionId": cid,
            "userId": "WEEK1_TEST",
            "role": "TEST",
            "connectedAt": datetime.now(timezone.utc).isoformat(),
            "expiresAt": int(time.time()) + 3600
        })
        return {"statusCode": 200, "body": "Connected"}
    if route == "$disconnect":
        table.delete_item(Key={"connectionId": cid})
        return {"statusCode": 200, "body": "Disconnected"}
    try:
        body = json.loads(event.get("body") or "{}")
        if not isinstance(body, dict):
            raise ValueError("Object required")
    except (ValueError, TypeError):
        body = {}
    request_id = body.get("requestId")
    item = table.get_item(
        Key={"connectionId": cid}, ConsistentRead=True
    ).get("Item")
    alive = item and int(item.get("expiresAt", 0)) > time.time()
    if not alive:
        msg = {"type": "RESPONSE", "requestId": request_id,
               "ok": False, "error": {"code": "UNAUTHORIZED"}}
    elif body.get("action") == "ping":
        msg = {"type": "RESPONSE", "requestId": request_id,
               "ok": True, "data": {"message": "pong"}}
    else:
        msg = {"type": "RESPONSE", "requestId": request_id,
               "ok": False, "error": {"code": "INVALID_REQUEST"}}
    endpoint = "https://" + rc["domainName"] + "/" + rc["stage"]
    client = boto3.client("apigatewaymanagementapi",
                          endpoint_url=endpoint)
    try:
        client.post_to_connection(
            ConnectionId=cid,
            Data=json.dumps(msg).encode("utf-8")
        )
    except client.exceptions.GoneException:
        table.delete_item(Key={"connectionId": cid})
    return {"statusCode": 200, "body": "Processed"}
