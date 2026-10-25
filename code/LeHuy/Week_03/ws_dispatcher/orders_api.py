import hashlib
import json
import os
import time
import boto3
from botocore.exceptions import ClientError
from common import APIError, orders, connections, tasks
from common import read, load_order, can_read, snapshot, utc

def describe(order):
    data = snapshot(order)
    running = order.get('workflowStatus') not in ('SUCCEEDED', 'FAILED', 'TIMED_OUT')
    if order.get('executionArn'):
        execution = boto3.client('stepfunctions').describe_execution(
            executionArn=order['executionArn'])
        data['executionStatus'] = execution['status']
        running = execution['status'] == 'RUNNING'
    before = {'ACCEPTED': 'PLACED', 'DELIVERING': 'ACCEPTED',
              'COMPLETED': 'DELIVERING'}
    ready = []
    for step, previous in before.items():
        task = read(tasks, {'orderId': order['orderId'], 'step': step})
        if (running and order['status'] == previous and task
                and task.get('taskState') == 'READY'
                and int(task.get('expiresAt', 0)) > time.time()
                and ('expectedVersion' not in task
                     or task['expectedVersion'] == order['version'])):
            ready.append(step)
    data['readySteps'] = ready
    return data

def create(body, actor):
    if actor['role'] != 'CUSTOMER':
        raise APIError('FORBIDDEN')
    items, address, req = body.get('items'), body.get('deliveryAddress'), body['requestId']
    if (not isinstance(items, list) or not 1 <= len(items) <= 20 or
            not isinstance(address, str) or not 5 <= len(address.strip()) <= 300):
        raise APIError('VALIDATION_ERROR')
    clean = []
    for item in items:
        if (not isinstance(item, dict) or not isinstance(item.get('name'), str) or
                not 1 <= len(item['name'].strip()) <= 100 or
                type(item.get('quantity')) is not int or not 1 <= item['quantity'] <= 20):
            raise APIError('VALIDATION_ERROR')
        clean.append({'name': item['name'].strip(), 'quantity': item['quantity']})
    oid = 'ORD-' + hashlib.sha256((actor['id'] + '\0' + req).encode()).hexdigest()[:24]
    intent = json.dumps({'items': clean, 'address': address.strip()}, sort_keys=True)
    signature = hashlib.sha256(intent.encode()).hexdigest()
    arn = os.environ.get('STATE_MACHINE_ARN', '')
    if not arn or len(arn.split(':')) != 7 or ':stateMachine:' not in arn:
        raise APIError('WORKFLOW_NOT_CONFIGURED')
    stamp = utc()
    item = {'orderId': oid, 'customerId': actor['id'], 'items': clean,
            'deliveryAddress': address.strip(), 'status': 'PLACED', 'version': 1,
            'workflowStatus': 'NOT_STARTED', 'createdAt': stamp, 'updatedAt': stamp,
            'createRequestId': req, 'createPayloadHash': signature}
    try:
        orders.put_item(Item=item, ConditionExpression='attribute_not_exists(orderId)')
    except ClientError as exc:
        if exc.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
        item = read(orders, {'orderId': oid})
        if not item or item.get('createPayloadHash') != signature:
            raise APIError('CONFLICT')
    if item.get('executionArn'):
        return describe(item)
    client = boto3.client('stepfunctions')
    input_text = json.dumps({'orderId': oid}, separators=(',', ':'))
    try:
        execution = client.start_execution(stateMachineArn=arn, name=oid,
                                            input=input_text)['executionArn']
    except ClientError as exc:
        if exc.response['Error']['Code'] == 'ExecutionAlreadyExists':
            execution = arn.replace(':stateMachine:', ':execution:') + ':' + oid
            prior = client.describe_execution(executionArn=execution)
            if json.loads(prior['input']) != {'orderId': oid}:
                raise APIError('CONFLICT')
        else:
            print('start_execution error=' + exc.response['Error']['Code'])
            try:
                orders.update_item(Key={'orderId': oid},
                    UpdateExpression='SET workflowStatus=:w',
                    ConditionExpression='attribute_not_exists(executionArn)',
                    ExpressionAttributeValues={':w': 'START_FAILED'})
            except ClientError:
                pass
            raise APIError('WORKFLOW_START_FAILED')
    orders.update_item(Key={'orderId': oid},
        UpdateExpression='SET executionArn=:e',
        ConditionExpression='attribute_exists(orderId) AND '
        '(attribute_not_exists(executionArn) OR executionArn=:e)',
        ExpressionAttributeValues={':e': execution})
    return describe(read(orders, {'orderId': oid}))

def handle_action(body, actor, cid):
    action = body.get('action')
    if action == 'ping':
        return {'message': 'pong'}
    if action == 'createOrder':
        return create(body, actor)
    if action in ('getOrder', 'subscribeOrder'):
        order = load_order(body.get('orderId'), actor)
        if action == 'subscribeOrder':
            connections.update_item(Key={'connectionId': cid},
                UpdateExpression='SET orderId=:o',
                ConditionExpression='attribute_exists(connectionId)',
                ExpressionAttributeValues={':o': order['orderId']})
            # Read snapshot after registration so reconnect gets current data.
            order = load_order(order['orderId'], actor)
        return describe(order)
    if action == 'listOrders':
        if actor['role'] != 'DRIVER':
            raise APIError('FORBIDDEN')
        args = {'Limit': 30, 'ConsistentRead': True}
        cursor = body.get('cursor')
        if cursor is not None:
            if (not isinstance(cursor, dict) or set(cursor) != {'orderId'} or
                    not isinstance(cursor['orderId'], str)):
                raise APIError('VALIDATION_ERROR')
            args['ExclusiveStartKey'] = cursor
        reply = orders.scan(**args)
        visible = [snapshot(o) for o in reply.get('Items', []) if can_read(actor, o)]
        return {'orders': visible, 'nextCursor': reply.get('LastEvaluatedKey')}
    if action == 'updateOrderStatus':
        if actor['role'] != 'DRIVER':
            raise APIError('FORBIDDEN')
        oid, step = body.get('orderId'), body.get('targetStatus')
        version, request = body.get('expectedVersion'), body['requestId']
        before = {'ACCEPTED': 'PLACED', 'DELIVERING': 'ACCEPTED',
                  'COMPLETED': 'DELIVERING'}
        if step not in before or type(version) is not int or version < 1:
            raise APIError('VALIDATION_ERROR')
        order = load_order(oid, actor)
        task = read(tasks, {'orderId': oid, 'step': step})
        same_done = (task and task.get('taskState') == 'DONE'
                     and task.get('requestId') == request
                     and task.get('actorId') == actor['id'])
        if not same_done:
            if step != 'ACCEPTED' and order.get('driverId') != actor['id']:
                raise APIError('FORBIDDEN')
            if order['status'] != before[step] or order['version'] != version:
                raise APIError('CONFLICT')
        # Adapter for TV1 submit deployed on 16 October: actorId, status/errorCode.
        event = {
            'orderId': oid,
            'targetStatus': step,
            'actorId': actor['id'],
            'requestId': request,
            'expectedVersion': version
        }
        name = os.environ.get('SUBMIT_LAMBDA_ARN', '')
        if not name:
            raise APIError('CALLBACK_NOT_CONFIGURED')
        reply = boto3.client('lambda').invoke(FunctionName=name,
            InvocationType='RequestResponse', Payload=json.dumps(event).encode())
        if reply.get('FunctionError'):
            raise APIError('CALLBACK_FAILED')
        output = json.loads(reply['Payload'].read() or b'{}')
        if not isinstance(output, dict):
            raise APIError('CALLBACK_FAILED')
        if not output.get('ok'):
            raise APIError(output.get('errorCode', 'CALLBACK_FAILED'))
        status = output.get('status')
        if status not in ('QUEUED', 'PROCESSING', 'ALREADY_DONE'):
            raise APIError('CALLBACK_FAILED')
        return {'submission': status, 'orderId': oid, 'step': step}
    raise APIError('INVALID_ACTION')
