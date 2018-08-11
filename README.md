
# CFN SQS SNS Custom subscriber

## Why

Currently, it's not possible to subscribe an SQS queue to an SNS topic from
another account and/or region using native CloudFormation resources.
This is a custom CloudFormation resource that will let you do that.

## What

This uses [AWS SAM](https://github.com/awslabs/serverless-application-model)
to deploy a custom CFN function which runs in Lambda.

## How

An example `template.yaml` is provided which creates a queue and subscribes it
to the topic specified in the parameters.

### Syntax

```yaml
Type: Custom::SnsSubscription
Properties:
  ServiceToken: String
  TopicArn: String
  Endpoint: String
```

### Properties

#### ServiceToken

The ARN for the Lambda function.

_Required_: Yes

_Type_: String

_Update requires_: Replacement

#### TopicArn

The ARN for the SNS topic the queue is being subscribed to.

_Required_: Yes

_Type_: String

_Update requires_: Replacement

#### Endpoint

The ARN for the SQS queue we are subscribing to the topic

_Required_: Yes

_Type_: String

_Update requires_: Replacement
