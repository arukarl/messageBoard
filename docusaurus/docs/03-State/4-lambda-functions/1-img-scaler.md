---
sidebar_position: 1
---

# Create Thumbnail

### Overview

After image has been upload to S3, Lambda function creates thumbnail to be displayed on messages list.

:::tip
While thumbnail is not ready, loading image is displayed:
<img src="/img/loading.gif" width="100"/>
:::


<img src="/img/create-thumbnail.svg" width="800"/>

### CloudFormation

Timeout has been increased from default 3s to 60s, because larger images need more than 3s.

```yaml title="base_stack.yaml"
  ImgScaler:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: img_scaler
      Code:
        S3Bucket: mb-conf-folder
        S3Key: img_scaler.zip
      Runtime: python3.8
      Role: !GetAtt LambdaRole.Arn
      PackageType: Zip
      Handler: img_scaler.lambda_handler
      Timeout: 60
      MemorySize: 256
      Layers:
        - !Ref Pillow

  LambdaS3Permission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ImgScaler
      Action: lambda:InvokeFunction
      Principal: s3.amazonaws.com
      SourceAccount: !Ref AWS::AccountId
      SourceArn: !GetAtt S3Bucket.Arn

  Pillow:
    Type: AWS::Lambda::LayerVersion
    Properties:
      LayerName: pillow
      Content:
        S3Bucket: mb-conf-folder
        S3Key: pillow_layer.zip
      CompatibleRuntimes:
        - python3.8
```

### Python code

##### Full code



```python title="img_scaler.py"
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

```
