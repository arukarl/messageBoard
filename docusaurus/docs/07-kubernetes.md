---
sidebar_position: 7

---

# Kubernetes

Kubernetes (K8s) gluster is installed with [**kOps**](https://github.com/kubernetes/kops).

<img src="/img/k8s.svg"/>

### Architectural choices

Main deviations from standard off-the-shelf config.

##### EC2 instances

Since this isn't business critical application 100% of instances are from spot bool, which allows 
discounted prices compared to On-Demand prices.

Instance type for one master node is `t3.small` and for 2 worker nodes `t3.micro`.


##### Ingress controller

NGINX ingress controller is deployed using DaemonSet, which deploys the controller on every node.
AWS Network load balancer is used to route traffic from karlaru.com and docs.karlaru.com to ingress controllers.
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-ingress
  namespace: nginx-ingress
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: "tcp"
    service.beta.kubernetes.io/aws-load-balancer-proxy-protocol: "*"
    service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  - port: 443
    targetPort: 443
    protocol: TCP
    name: https
  selector:
    app: nginx-ingress
```


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

