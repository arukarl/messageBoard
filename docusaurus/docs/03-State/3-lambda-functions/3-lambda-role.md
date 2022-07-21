---
sidebar_position: 3
---

# Lambda IAM Role

### Overview

Grants permissions to Lambda functions.
Resources and actions are as limited as possible for security reasons.

### CloudFormation code snippet

```yaml title="base_stack.yaml"
  LambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - lambda.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      Policies:
        - PolicyName: lambda-role
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action: [
                          "s3:PutObject",
                          "s3:GetObject",
                          "s3:DeleteObject",
                          "sqs:GetQueueUrl",
                          "sqs:GetQueueAttributes",
                          "sqs:ReceiveMessage",
                          "sqs:SendMessage",
                          "sqs:DeleteMessage",
                          "sqs:PurgeQueue",
                          "dynamodb:UpdateItem",
                          "dynamodb:DescribeStream",
                          "dynamodb:GetRecords",
                          "dynamodb:GetShardIterator",
                          "dynamodb:ListStreams",
                          "logs:CreateLogGroup",
                          "logs:CreateLogStream",
                          "logs:PutLogEvents"
                        ]
                Resource: [
                          "arn:aws:s3:::karlaru-mb/*",
                          "arn:aws:sqs:eu-north-1:978039897892:image_rezised",
                          "arn:aws:sqs:eu-north-1:978039897892:delete-image",
                          "arn:aws:dynamodb:eu-north-1:978039897892:table/messages",
                          "arn:aws:dynamodb:eu-north-1:978039897892:table/messages/stream/*",
                          "arn:aws:logs:eu-north-1:978039897892:log-group:/aws/*"
                        ]
```
