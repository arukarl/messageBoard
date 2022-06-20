import boto3
import json

s3_bucket = 'karlaru-mb'
aws_region = "eu-north-1"

s3_client = boto3.client('s3', region_name=aws_region)


def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        img_name = body['image_name']
        s3_client.delete_objects(Bucket=s3_bucket,
                                 Delete={'Objects': [{'Key': 'images/' + img_name}, {'Key': 'thumbnails/' + img_name}]})
