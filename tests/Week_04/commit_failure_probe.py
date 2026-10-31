import copy
import hashlib
import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
import boto3

REGION = 'us-east-1'
ACCOUNT = '053151184394'

session = boto3.Session(region_name=REGION)
assert session.client('sts').get_caller_identity()['Account'] == ACCOUNT, f"Account mismatch, expected {ACCOUNT}"

sfn = session.client('stepfunctions')
db = session.resource('dynamodb')
orders = db.Table('fooddelivery-orders')
tasks = db.Table('fooddelivery-workflow-tasks')

main_arn = (
    f'arn:aws:states:{REGION}:{ACCOUNT}:'
    'stateMachine:fooddelivery-order-workflow'
)
live = sfn.describe_state_machine(stateMachineArn=main_arn)
source = json.loads(live['definition'])['States']
assert live['type'] == 'STANDARD'

for name in ('HandleWorkflowError', 'PersistWorkflowFailure',
             'WorkflowFailed', 'CommitAcceptedTransition'):
    assert name in source, f'Missing state: {name}'

assert source['HandleWorkflowError']['Next'] == 'PersistWorkflowFailure'
assert any(
    'States.ALL' in c['ErrorEquals']
    and c['Next'] == 'HandleWorkflowError'
    for c in source['CommitAcceptedTransition'].get('Catch', [])
)

states = {
    name: copy.deepcopy(source[name])
    for name in ('HandleWorkflowError', 'PersistWorkflowFailure',
                 'WorkflowFailed', 'CommitAcceptedTransition')
}
commit = states['CommitAcceptedTransition']
commit['Next'] = 'UnexpectedCommitSuccess'
commit['TimeoutSeconds'] = 30
states['UnexpectedCommitSuccess'] = {'Type': 'Succeed'}

definition = {
    'Comment': 'W4 isolated commit claim failure probe',
    'QueryLanguage': 'JSONPath',
    'StartAt': 'CommitAcceptedTransition',
    'States': states
}
text = json.dumps(definition)
validation = sfn.validate_state_machine_definition(
    definition=text, type='STANDARD')
assert validation['result'] == 'OK', validation['diagnostics']

suffix = uuid.uuid4().hex[:12]
sm_name = 'fooddelivery-w4-commit-failure-' + suffix
execution_name = 'W4-FAIL-' + suffix
oid = 'ORD-' + hashlib.sha256(sm_name.encode()).hexdigest()[:24]
request = 'W4-FAIL-' + suffix

created = sfn.create_state_machine(
    name=sm_name, definition=text,
    roleArn=live['roleArn'], type='STANDARD')
sm_arn = created['stateMachineArn']
execution_arn = sm_arn.replace(':stateMachine:', ':execution:')
execution_arn += ':' + execution_name
stamp = datetime.now(timezone.utc).isoformat()

report = {
    'orderId': oid, 'requestId': request,
    'stateMachineArn': sm_arn, 'executionArn': execution_arn,
    'createdAt': stamp, 'evaluation': 'PENDING',
    'scope': 'Commit claim guard and Catch persistence only'
}
Path('w4-commit-failure-result.json').write_text(
    json.dumps(report, indent=2), encoding='utf-8')
print('TEST WORKFLOW:', sm_arn)
print('ORDER:', oid)

orders.put_item(
    Item={
        'orderId': oid, 'customerId': 'C001',
        'status': 'PLACED', 'version': 1,
        'workflowStatus': 'RUNNING',
        'executionArn': execution_arn,
        'createdAt': stamp, 'updatedAt': stamp,
        'testCase': 'W4-TC03'
    },
    ConditionExpression='attribute_not_exists(orderId)')

tasks.put_item(
    Item={
        'orderId': oid, 'step': 'ACCEPTED',
        'taskState': 'CLAIMED', 'actorId': 'D001',
        'requestId': request, 'createdAt': int(time.time()),
        'expiresAt': int(time.time()) + 1800,
        'testCase': 'W4-TC03'
    },
    ConditionExpression='attribute_not_exists(orderId)')

sfn.start_execution(
    stateMachineArn=sm_arn, name=execution_name,
    input=json.dumps({
        'orderId': oid,
        'transitionResult': {
            'actorId': 'D002', 'requestId': request
        }
    }))

execution = {}
for attempt in range(20):
    execution = sfn.describe_execution(executionArn=execution_arn)
    if execution['status'] != 'RUNNING':
        break
    time.sleep(2)

order = orders.get_item(
    Key={'orderId': oid}, ConsistentRead=True)['Item']
task = tasks.get_item(
    Key={'orderId': oid, 'step': 'ACCEPTED'},
    ConsistentRead=True)['Item']

persist_ok = False
commit_failed = False
for page in sfn.get_paginator('get_execution_history').paginate(
        executionArn=execution_arn, includeExecutionData=False):
    events = page.get('events', [])
    for event in events:
        if event['type'] == 'TaskStateExited':
            details = event.get('stateExitedEventDetails', {})
            if details.get('name') == 'PersistWorkflowFailure':
                persist_ok = True
        if event['type'] in ('TaskFailed', 'LambdaFunctionFailed'):
            commit_failed = True

checks = {
    'executionFailed': execution.get('status') == 'FAILED',
    'commitRejected': commit_failed,
    'persistenceSucceeded': persist_ok,
    'businessStatusUnchanged': order.get('status') == 'PLACED',
    'versionUnchanged': int(order.get('version', 0)) == 1,
    'workflowFailedPersisted': order.get('workflowStatus') == 'FAILED',
    'endedAtPresent': bool(order.get('workflowEndedAt')),
    'taskNotCommitted': task.get('taskState') == 'CLAIMED',
    'claimOwnerUnchanged': task.get('actorId') == 'D001'
}

report.update({
    'executionStatus': execution.get('status'),
    'checks': checks,
    'evaluation': (
        'PENDING' if execution.get('status') == 'RUNNING'
        else 'PASS' if all(checks.values()) else 'FAIL'
    )
})

Path('w4-commit-failure-result.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))

