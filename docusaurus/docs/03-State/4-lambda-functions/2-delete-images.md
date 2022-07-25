---
sidebar_position: 2
---

# Delete Images

### Overview

This function deletes images after message is deleted.

<img src="/img/delete-img.svg" width="800"/>

### Cloudformation

It waits `MaximumBatchingWindowInSeconds: 120`s before executing. 
So if users delete many messages in 120s window, related images will be removed as a batch. 
This reduces number of cold starts.

```yaml title="base_stack.yaml"
  ImgDeleter:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: delete-image
      Code:
        S3Bucket: mb-conf-folder
        S3Key: img_delete.zip
      Runtime: python3.9
      Role: !GetAtt LambdaRole.Arn
      PackageType: Zip
      Handler: img_delete.lambda_handler

  ImagesDeleteTrigger:
    Type: AWS::Lambda::EventSourceMapping
    Properties:
      BatchSize: 100
      MaximumBatchingWindowInSeconds: 120
      Enabled: true
      EventSourceArn: !GetAtt MessagesTable.StreamArn
      FunctionName: !Ref ImgDeleter
      StartingPosition: LATEST
```
### Python code

```python title="img_delete.py"
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

```
