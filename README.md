# Message Board app

### Live Deployments:

Nginx on EC2: [nginx.karlaru.com](https://nginx.karlaru.com)

messageBoard on K8s: [karlaru.com](https://karlaru.com)

Docs on K8s: [docs](https://docs.karlaru.com)

<hr>

### How to deploy?

**Deploy state stack**

`bash deploy_base_stack.sh`

**Deploy ec2 with nginx**

`bash deploy_nginx.sh`

**Deploy Kubernetes cluster**

`bash deploy_kubernetes.sh`

**Build-Deploy messageBoard**

`bash build_messageboard.sh`

**Build-Deploy docs**

`bash build_docs.sh`

**Update Lambda Functions**

`bash update_lambda_fuctions.sh`
