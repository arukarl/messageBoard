---
sidebar_position: 1
---

# Overview

Kubernetes (K8s) gluster is installed with [**kOps**](https://github.com/kubernetes/kops).

<img src="/img/k8s.svg"/>

### Architectural choices

##### EC2 instances

Since this isn't business critical application 100% of instances are from spot bool, which allows 
discounted prices compared to On-Demand prices.

Instance type for one master node is `t3.small` and for 2 worker nodes `t3.micro`.

##### Pod IAM role

kOps publishes K8s service account token issuer and configures
AWS to trust it to authenticate K8s service account. 
All pods, that have `serviceAccountName: iam-account` config value,
have access to created IAM role. 
This enables using **Boto3** with assumed AWS credentials.

```yaml 
kind: Cluster
spec:
    iam:
    serviceAccountExternalPermissions:
      - name: iam-account
        namespace: default
        aws:
          inlinePolicy: |-
            [
              {
                "Effect": "Allow",
                "Action": [
                    "s3:PutObject",
                    "dynamodb:PutItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:GetItem",
                    "dynamodb:Scan"
                ],
                "Resource": [
                    "arn:aws:s3:::karlaru-mb/*",
                    "arn:aws:dynamodb:eu-north-1:978039897892:table/messages",
                    "arn:aws:dynamodb:eu-north-1:978039897892:table/users"
                ]
              }
            ]
```

```yaml 
kind: ServiceAccount
metadata:
  name: iam-account
  namespace: default
  
---

kind: Deployment
spec:
  template:
    spec:
      serviceAccountName: iam-account
```

