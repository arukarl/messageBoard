---
sidebar_position: 7

---

# Kubernetes

Kubernetes (K8s) gluster is installed with [**kOps**](https://github.com/kubernetes/kops).

<img src="/img/k8s.svg"/>

### Architectural choices

Main deviations from standard off-the-shelf config.

#### EC2 instances

Since this isn't business critical application 100% of instances are from spot bool, which allows 
discounted prices compared to On-Demand prices.

Instance type for one master node is `t3.small` and for 2 worker nodes `t3.micro`.


#### Ingress controller

NGINX ingress controller is deployed using DaemonSet, which deploys the controller on every node.
**AWS Network Load Balancer** is used to route traffic from **karlaru.com** and **docs.karlaru.com** to 
ingress controllers on each node. 

Both URL-s point to same load-balancer/IP
```bash
$ nslookup karlaru.com
Non-authoritative answer:
Name:   karlaru.com
Address: 13.50.43.217

$ nslookup docs.karlaru.com
Non-authoritative answer:
Name:   docs.karlaru.com
Address: 13.50.43.217
```


:::tip
Thanks to ingress controller **only 1 load-balancer** can be used,  reducing unnecessary costs. 
:::

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

An Ingress object describes which url routes to which service:

```yaml title="simplified version of ingress.yaml"
kind: Ingress
spec:
  rules:
    - host: karlaru.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: messageboard
                port:
                  number: 5000
    - host: docs.karlaru.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: docs
                port:
                  number: 3000
```


#### Flask configuration parameters

Flask configuration is stored as a secret created by

```bash
kubectl create secret generic flask-conf --from-file=../secrets/conf.cfg
```

and mounted to container as file:

```yaml
        volumeMounts:
          - mountPath: "/messageBoard/conf.cfg"
            name: flask-conf
            subPath: conf.cfg
            readOnly: true

      volumes:
      - name: flask-conf
        secret:
            secretName: flask-conf
```

#### SSL certificate

A wildcard (multiple subdomains) SSL certificate from CA **Sectigo** is stored as a secret

```bash
kubectl create secret tls main-tls --key="../secrets/SectigoSSL.key" --cert="../secrets/SectigoSSL.crt"
```

and added to ingress controllers, which terminate TLS. 
So all traffic from Client browser to a node is TLS-encrypted.

```yaml

kind: Ingress
metadata:
  name: ingress-mb
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - karlaru.com
      secretName: main-tls
```

#### Pod IAM role

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
      containers:
      - name: mb
        image: karlaru/message-board
        imagePullPolicy: Always
        ports:
          - name: tcp
            containerPort: 5000
```

