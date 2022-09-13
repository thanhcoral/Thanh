# import boto3
import json
import logging
from termcolor import colored
logger = logging.getLogger()
logger.setLevel(logging.INFO)


REGION = 'ap-northeast-1'
ECS_CLUSTER = 'tai-test-ci-tools'
LAMBDA_UPDATE_TASK = 'arn:aws:lambda:ap-northeast-1:012881927014:function:anhtt_update_task'
LAMBDA_CHECK_AND_SCAN = 'arn:aws:lambda:ap-northeast-1:012881927014:function:anhtt_check_and_scan'

event = {
    'task_arn': 'arn:aws:ecs:ap-northeast-1:012881927014:task/mycluster/043de9ab06bb41d29e97576f1f1d1d33',
    'type': 'SELENIUM',
}



def lambda_handler(event, context):
    print(json.dumps(event))
    # task_id = get_record_id(event['task_arn'])
    
    container_family = event['task_arn'].split(':')[-2].split('/')[-1]
    if event.get('type') == 'SELENIUM':
        # get_ecs_task_id(container_family)
        container_name, container_id = get_ecs_task_id(container_family)
        log_stream = 'ecs/' + container_name + '/' + container_id
    else:
        log_stream = 'ecs/'
    
    # payload = {'taskids': task_id, 'status': 'COMPLETED', 'type': event.get('type'), 'log_stream': log_stream}
    
    # call_lambda(LAMBDA_UPDATE_TASK, payload)
    # call_lambda(LAMBDA_CHECK_AND_SCAN, {})
    
    print(colored('thanh', 'green'))
    print(colored(log_stream, 'green'))
    



def get_record_id(task_arn):
    client = boto3.client('ecs', region_name=REGION)
    logger.info(f'Getting tag of ECS task {task_arn}')
    response = client.describe_task_definition(
        taskDefinition=task_arn,
        include=[
            'TAGS',
        ]
    )
    return response['tags'][0]['value']

def get_ecs_task_id(family):
    # client = boto3.client('ecs', region_name=REGION)
    print(colored(f'Getting task id of ECS task {family}', 'blue'))
    # response = client.list_tasks(
    #     cluster=ECS_CLUSTER,
    #     family=family,
    #     desiredStatus='STOPPED'
    # )
    
    # response2 = client.describe_tasks(
    #     cluster=ECS_CLUSTER,
    #     tasks=[
    #         response['taskArns'][0]
    #     ]
    # )
    return ['123123213', '9808908908']
    # return [response2['tasks'][0]['containers'][0]['name'], response['taskArns'][0].split(':')[-1].split('/')[-1]]

def call_lambda(name, payload):
    client = boto3.client('lambda', region_name=REGION)
    logger.info(f'Calling lambda: {name}')
    return client.invoke(
        FunctionName=name,
        InvocationType='Event',
        Payload=json.dumps(payload)
    )


lambda_handler(event, {})