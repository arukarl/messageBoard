export KOPS_STATE_STORE=s3://karl-aru-mb-state

# kops export kubecfg --admin

kops create -f k8s/cluster-deployment.yaml

kops create -f k8s-deployment.yaml --yes --admin

kops validate cluster --wait 15m

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.0/deploy/static/provider/aws/deploy.yaml

kubectl apply -f  k8s/aws_secret.yaml

kubectl apply -f k8s/deployment.yaml

kubectl create secret tls main-tls --key="mb-conf-folder/nginx_GeoTrust.key" --cert="mb-conf-folder/nginx_GeoTrust.crt"

kubectl apply -f k8s/ingress.yaml

# Change Route 53 record

