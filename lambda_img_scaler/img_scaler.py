import boto3
import json
from PIL import Image

# Thumbnail size
size = (150, 150)
s3_bucket = 'karlaru-mb'
aws_region = "eu-north-1"

s3_client = boto3.client('s3', region_name=aws_region)
sqs_client = boto3.client('sqs', region_name=aws_region)


def lambda_handler(event, context):
    # There is only one element in event['Records'], so 'for' loop not needed
    img_name = event['Records'][0]['s3']['object']['key'].split("/")[1]
    download_path = '/tmp/{}'.format(img_name)
    upload_path = '/tmp/resized-{}'.format(img_name)

    # Download img from s3 to local temp folder
    s3_client.download_file(s3_bucket, "images/" + img_name, download_path)
    # Reduce image to 150x150 with Pillow
    with Image.open(download_path) as image:
        image.thumbnail(size)
        image.save(upload_path, quality=95)
    # Upload smaller image the different S3 bucket
    s3_client.upload_file(upload_path, s3_bucket, "thumbnails/" + img_name,
                          ExtraArgs={'CacheControl': 'max-age=2592000, public'})
    # Get dynamodb message_id for current image
    image_metadata = s3_client.head_object(Bucket=s3_bucket, Key="images/" + img_name)['ResponseMetadata'][
        'HTTPHeaders']
    message_id = image_metadata['x-amz-meta-message_id']

    # New url to resized image
    new_url = "https://d2uj644jlhz1yf.cloudfront.net/" + "thumbnails/" + img_name

    sqs_client.send_message(QueueUrl='https://sqs.eu-north-1.amazonaws.com/978039897892/image_rezised',
                            MessageBody=json.dumps({
                                "message_id": message_id,
                                "new_location": new_url
                            }))