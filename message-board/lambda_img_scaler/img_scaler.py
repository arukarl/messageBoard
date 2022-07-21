import boto3
from PIL import Image

# Thumbnail size
size = (150, 150)

# AWS resources
s3_bucket = 'karlaru-mb'
aws_region = "eu-north-1"

s3_client = boto3.client('s3', region_name=aws_region)
sqs_client = boto3.client('sqs', region_name=aws_region)
dynamodb = boto3.resource('dynamodb', region_name="eu-north-1")
db_table = dynamodb.Table("messages")


def lambda_handler(event, context):
    for record in event["Records"]:
        img_name = record['s3']['object']['key'].split("/")[1]
        download_path = '/tmp/{}'.format(img_name)
        upload_path = '/tmp/resized-{}'.format(img_name)

        s3_client.download_file(s3_bucket, "images/" + img_name, download_path)

        with Image.open(download_path) as image:
            image.thumbnail(size)
            image.save(upload_path, quality=95)

        s3_client.upload_file(upload_path, s3_bucket, "thumbnails/" + img_name,
                              ExtraArgs={'CacheControl': 'max-age=2592000, public'})

        image_metadata = s3_client.head_object(Bucket=s3_bucket,
                                               Key="images/" + img_name)['ResponseMetadata']['HTTPHeaders']

        message_id = image_metadata['x-amz-meta-message_id']

        db_table.update_item(Key={'message_id': message_id},
                             UpdateExpression="set thumbnail = :i",
                             ExpressionAttributeValues={':i': 'true'})
