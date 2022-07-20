---
sidebar_position: 1
---

# Create Thumbnail

After upload to S3, create thumbnail

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
