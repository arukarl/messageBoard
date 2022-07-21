import boto3

s3_bucket = 'karlaru-mb'
aws_region = "eu-north-1"
s3_client = boto3.client('s3', region_name=aws_region)


def lambda_handler(event, context):
    for record in event["Records"]:

        eventName = record["eventName"]

        if eventName == "REMOVE":
            img_name = record["dynamodb"]["OldImage"]["img"]["S"]

            s3_client.delete_objects(Bucket=s3_bucket,
                                     Delete={'Objects': [
                                         {'Key': 'images/' + img_name},
                                         {'Key': 'thumbnails/' + img_name}
                                     ]})
