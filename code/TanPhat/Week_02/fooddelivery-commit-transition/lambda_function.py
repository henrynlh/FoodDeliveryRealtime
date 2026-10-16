import os
import json
import time
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
sns_client = boto3.client('sns', region_name='us-east-1')

ORDERS_TABLE = os.environ.get('ORDERS_TABLE', 'fooddelivery-orders')
TASKS_TABLE = os.environ.get('WORKFLOW_TASKS_TABLE', 'fooddelivery-workflow-tasks')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

orders_table = dynamodb.Table(ORDERS_TABLE)
tasks_table = dynamodb.Table(TASKS_TABLE)

def lambda_handler(event, context):
    print("Commit transition event:", json.dumps(event))
    
    order_id = event.get('orderId')
    step = event.get('step')
    actor_id = event.get('actorId')
    request_id = event.get('requestId')
    now = int(time.time())
    
    # 1. Cập nhật bảng Orders
    update_expr = "SET #st = :step, updatedAt = :now, lastTransitionRequestId = :req"
    expr_names = {'#st': 'status'}
    expr_vals = {
        ':step': step,
        ':now': now,
        ':req': request_id
    }
    
    if step == 'ACCEPTED':
        update_expr += ", driverId = :driver"
        expr_vals[':driver'] = actor_id
        
    # Tăng version
    update_expr += " ADD version :inc"
    expr_vals[':inc'] = 1
    
    orders_table.update_item(
        Key={'orderId': order_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_vals
    )
    print(f"Orders table updated to {step} for order {order_id}")
    
    # 2. Đánh dấu taskState = DONE trong WorkflowTasks
    try:
        tasks_table.update_item(
            Key={'orderId': order_id, 'step': step},
            UpdateExpression="SET taskState = :done",
            ExpressionAttributeValues={':done': 'DONE'}
        )
    except Exception as ex:
        print(f"Warning: Failed to mark task as DONE: {str(ex)}")

    # 3. Gửi SNS nếu ở ACCEPTED hoặc COMPLETED
    if step in ['ACCEPTED', 'COMPLETED'] and SNS_TOPIC_ARN:
        try:
            msg = {
                "orderId": order_id,
                "status": step,
                "actorId": actor_id,
                "timestamp": now
            }
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"FoodDelivery: Order {order_id} is now {step}",
                Message=json.dumps(msg)
            )
            print(f"SNS notification published for {step}")
        except Exception as ex:
            print(f"Failed to publish SNS: {str(ex)}")
            
    return {
        "ok": True,
        "orderId": order_id,
        "step": step,
        "status": "COMMITTED"
    }