import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name="eu-north-1")
db_table = dynamodb.Table("messages")


def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])

        message_id = body['message_id']

        db_table.update_item(Key={'message_id': message_id},
                             UpdateExpression="set thumbnail = :i",
                             ExpressionAttributeValues={':i': 'true'})
