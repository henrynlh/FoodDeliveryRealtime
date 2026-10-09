import json
import logging
import os
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    if not isinstance(event, dict):
        raise ValueError("Event must be a JSON object")
    mode = event.get("mode", "echo")
    order_id = event.get("orderId", "TEST-W1-001")
    # Never log the entire event. Callback events include a task token.
    logger.info("foundation mode=%s orderId=%s", mode, order_id)

    if mode == "echo":
        return {"ok": True, "mode": mode, "orderId": order_id}

    if mode == "sns":
        topic_arn = os.environ.get("SNS_TOPIC_ARN")
        if not topic_arn:
            raise ValueError("Set SNS_TOPIC_ARN in Lambda environment variables")
        response = boto3.client("sns").publish(
            TopicArn=topic_arn,
            Subject="FoodDelivery Week 1 test",
            Message=json.dumps({"orderId": order_id, "test": "WEEK1_ONLY"}),
        )
        return {"ok": True, "mode": mode, "messageId": response["MessageId"]}

    if mode == "callback":
        token = event.get("taskToken")
        if not token:
            raise ValueError("Run callback mode through Step Functions, not a manual Lambda test")
        output = {"ok": True, "test": "CALLBACK_PERMISSION_CHECK", "orderId": order_id}
        boto3.client("stepfunctions").send_task_success(
            taskToken=token,
            output=json.dumps(output),
        )
        # This self-callback proves capability, not a real human waiting flow.
        return {"callbackSubmitted": True}

    raise ValueError("Supported modes are echo, sns and callback")
