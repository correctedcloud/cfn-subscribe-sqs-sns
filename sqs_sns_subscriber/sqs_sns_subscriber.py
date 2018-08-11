import boto3
import json
import os
from botocore.vendored import requests

def send_response(response_url, response_dict):
    print("Sending response to CFN via S3")
    print(response_dict)
    r = requests.put(response_url, data=json.dumps(response_dict))
    print("Sent response to S3, got", r.status_code)

def lambda_handler(event, context):
    print(event)
    response_dict = {
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            }
    response_url = event['ResponseURL']
    resource_properties = event.get('ResourceProperties', {})
    (topic_arn, endpoint, sns_region) = check_resource_properties(
            resource_properties, response_dict)

    sns_client = boto3.client('sns', region_name=sns_region)

    if event.get('RequestType') == 'Create':
        subscription_arn = subscribe_queue_to_topic(sns_client, endpoint, topic_arn)
        if subscription_arn:
            response_dict['Status'] = 'SUCCESS'
            response_dict['PhysicalResourceId'] = subscription_arn
            send_response(response_url, response_dict)
            return response_dict
        else:
            response_dict['Status'] = 'FAILED'
            response_dict['Reason'] = 'Error subscribing queue to topic'
            send_response(response_url, response_dict)
            return response_dict

    if event.get('RequestType') == 'Delete':
        unsubscribe_queue_from_topic(sns_client, event['PhysicalResourceId'])
        response_dict['Status'] = 'SUCCESS'
        response_dict['PhysicalResourceId'] = event['PhysicalResourceId']
        send_response(response_url, response_dict)
        return response_dict

    if event.get('RequestType') == 'Update':
        unsubscribe_queue_from_topic(sns_client, event['PhysicalResourceId'])
        subscription_arn = subscribe_queue_to_topic(sns_client, endpoint, topic_arn)
        if subscription_arn:
            response_dict['Status'] = 'SUCCESS'
            response_dict['PhysicalResourceId'] = subscription_arn
            send_response(response_url, response_dict)
            return response_dict
        else:
            response_dict['Status'] = 'FAILED'
            response_dict['Reason'] = 'Error subscription queue to topic'
            send_response(response_url, response_dict)
            return response_dict
    raise

def subscribe_queue_to_topic(sns_client, endpoint, topic_arn):
    result = None
    try:
        result = sns_client.subscribe(
                TopicArn=topic_arn,
                Endpoint=endpoint,
                Protocol='sqs',
                )
    except Exception as e:
        print(e)
        return None
    print(result)
    return result['SubscriptionArn']

def unsubscribe_queue_from_topic(sns_client, subscription_arn):
    try:
        sns_client.unsubscribe(SubscriptionArn=subscription_arn)
    except:
        print("Error unsubscribing")
    return

def region_from_arn(arn):
    try:
        region = arn.split(':')[3]
        return region
    except:
        return None

def check_resource_properties(resource_properties, response_dict):
    topic_arn = resource_properties.get('TopicArn')
    endpoint = resource_properties.get('Endpoint')
    if not (topic_arn and endpoint):
        response_dict['Status'] = 'FAILED'
        response_dict['Reason'] = 'Missing required parameters'
        send_response(response_url, response_dict)
        return response_dict
    sns_region = region_from_arn(topic_arn)
    if not sns_region:
        response_dict['Status'] = 'FAILED'
        response_dict['Reason'] = 'Topic ARN format invalid'
        send_response(response_url, response_dict)
        return response_dict
    return (topic_arn, endpoint, sns_region)
