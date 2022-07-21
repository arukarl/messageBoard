---
sidebar_position: 3
---

# DynamoDB

### Users table

##### Schema

| Attribute name     | Type   | Description         |
|--------------------|--------|---------------------|
| id (Partition Key) | String | Google account ID   |
| username           | String | Google account name |

##### CloudFormation template snippet

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

Messages table has DynamoDB Streams enabled. When the table is modified, information is written to the stream.
When database record is deleted, i.e. `eventName == "REMOVE"`, 
then [**Delete Images**](lambda-functions/delete-images) Lambda function deletes all images related to this message as well.

##### Schema

| Attribute name             | Type   | Description                 |
|----------------------------|--------|-----------------------------|
| message_id (Partition Key) | String | uuid.uuid4()                |
| img                        | String | uuid.uuid4().file_type      |
| author                     | String | New image form              |
| description                | String | New image form              |
| location                   | String | New image form              |
| google_id                  | String | Author Google account ID    |
| timestamp                  | String | Post time                   |
| thumbnail                  | String | Has thumbnail been created? |


##### CloudFormation template snippet

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
