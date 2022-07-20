---
sidebar_position: 2
---

# Delete Images

Delete images Lambda function
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
      MaximumBatchingWindowInSeconds: 5
      Enabled: true
      EventSourceArn: !GetAtt MessagesTable.StreamArn
      FunctionName: !Ref ImgDeleter
      StartingPosition: LATEST
```
