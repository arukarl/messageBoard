---
sidebar_position: 3
---

# DynamoDB

### Users table

```yaml title="base_stack.yaml"
  UsersTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: users
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
```

### Messages table

```yaml title="base_stack.yaml"
  MessagesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: messages
      AttributeDefinitions:
        - AttributeName: message_id
          AttributeType: S
      KeySchema:
        - AttributeName: message_id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: OLD_IMAGE
```
