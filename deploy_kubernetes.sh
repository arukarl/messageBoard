cd kubernetes || exit

export KOPS_STATE_STORE=s3://karl-aru-mb-state

kops create -f cluster-deployment.yaml

kops update cluster --name karlaru.com --yes --admin

kops validate cluster --wait 15m

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.2.0/deploy/static/provider/aws/deploy.yaml

kubectl create secret tls main-tls --key="../secrets/SectigoSSL.key" --cert="../secrets/SectigoSSL.crt"

kubectl create secret generic flask-conf --from-file=../message-board/conf.cfg

kubectl apply -f deployment-mb.yaml

kubectl apply -f deployment-docs.yaml

echo "Waiting 60s before appling ingress"
sleep 60
kubectl apply -f ingress.yaml

echo "Waiting 60s to get load balancer URL"
sleep 60

printf "\nAdd\n"
echo "$(kubectl get ingress -o=jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}')"
echo "to Route53 hosted zone (karlaru.com) records:"
echo "karlaru.com"
echo "docs.karlaru.com"
