# import boto3
from termcolor import colored
import json
# import urllib3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = 'ap-northeast-1'
DYNAMO_DB = 'user-api'

SG_ID = 'sg-028cb74573c238ddd'

ECS_LOG_GROUP = '/ecs/7148_test-dast'
ECS_LOG_STREAM = 'ecs/'

# Task API
API_MAPPING = {
    'SAST': 'https://microscan.teamci.work/api/scan/subtask/',
    'CLOC': 'https://microscan.teamci.work/api/cloc/task/',
    'DAST': 'https://microscan.teamci.work/api/dast/task/',
    'SELENIUM': 'https://microscan.teamci.work/api/autotest/subtask/',
    'DEPENDENCY': 'https://microscan.teamci.work/api/dependency/task/'
}

event = {
    'taskids': '1212121,34343434,565656565',
    'type': 'SAST',
    'log_stream': '1516',
    'status': 'PENDING'
}

def lambda_handler(event, context):
    print(json.dumps(event))
    scan_type = event['type']
    api_path = API_MAPPING.get(scan_type)
    if not api_path:
        logger.error(f'Invalid scan type: {scan_type}')
        return
    
    log_stream = event.get('log_stream', ECS_LOG_STREAM)
    
    task_ids = event['taskids'].split(',')
    
    print(colored('Open ALB before get token', 'green'))
    # update_security_group_rule(True)
    
    for task_id in task_ids:
        update_status = (
            scan_type,
            api_path,
            task_id,
            event['status'],
            log_stream
        )
        # print(colored('update status', 'blue'))
        print(colored(update_status, 'blue'))

    
    print(colored('Close ALB after get token', 'green'))
    # update_security_group_rule(False)

def update_status(scan_type, api_path, task_id, status, log_stream):
    api = api_path + task_id
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    data = {'status': status}
    
    if scan_type == 'SELENIUM':
        data['log_group'] = ECS_LOG_GROUP
        data['log_stream'] = log_stream

    http = urllib3.PoolManager()
    response = http.request('PUT', api, fields=data, headers=headers)
    if response.status != 200:
        logger.error(f'Error when update task status: {response.data}')
    else:
        logger.info('Update task successfully')


def get_token():
    logger.info('Getting token from dynamodb')
    # dynamodb = boto3.resource('dynamodb', region_name=REGION)
    table = dynamodb.Table('user-api')
    response = table.get_item(Key={'id': 'task_api_token'})

    return response['Item']['token']

def update_security_group_rule(is_open):
    # client = boto3.client('ec2', region_name=REGION)
    
    # try:
    #     if is_open:
    #         response = client.authorize_security_group_ingress(
    #             GroupId=SG_ID,
    #             IpPermissions=[
    #                 {
    #                     'IpProtocol': 'tcp',
    #                     'FromPort': 443,
    #                     'ToPort': 443,
    #                     'IpRanges': [
    #                         {
    #                             'CidrIp': '0.0.0.0/0'
    #                         }
    #                     ]
    #                 }
    #             ]
    #         )
    #     else:
    #         response = client.revoke_security_group_ingress(
    #             GroupId=SG_ID,
    #             IpPermissions=[
    #                 {
    #                     'IpProtocol': 'tcp',
    #                     'FromPort': 443,
    #                     'ToPort': 443,
    #                     'IpRanges': [
    #                         {
    #                             'CidrIp': '0.0.0.0/0'
    #                         }
    #                     ]
    #                 },
    #             ]
    #         )
    # except Exception as e:
    #     logger.error(e)
    pass

lambda_handler(event, {})