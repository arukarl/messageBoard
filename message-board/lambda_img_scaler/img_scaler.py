import boto3
from PIL import Image
import mimetypes

# Thumbnail size
size = (150, 150)

# AWS resources
s3_bucket = 'karlaru-mb'
aws_region = "eu-north-1"

s3_client = boto3.client('s3', region_name=aws_region)


def lambda_handler(event, context):
    for record in event["Records"]:
        img_name = record['s3']['object']['key'].split("/")[1]
        download_path = '/tmp/{}'.format(img_name)
        upload_path = '/tmp/resized-{}'.format(img_name)

        s3_client.download_file(s3_bucket, "images/" + img_name, download_path)

        with Image.open(download_path) as image:
            image.thumbnail(size)
            image.save(upload_path, quality=95)

        content_type = mimetypes.guess_type(upload_path)[0]

        s3_client.upload_file(upload_path, s3_bucket, "thumbnails/" + img_name,
                              ExtraArgs={'CacheControl': 'max-age=2592000, public',
                                         'ContentType': content_type})
