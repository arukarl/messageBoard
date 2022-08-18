cd kubernetes || exit

export KOPS_STATE_STORE=s3://karl-aru-mb-state

kops create -f cluster-deployment.yaml

kops update cluster --name karlaru.com --yes --admin

kops validate cluster --wait 15m

kubectl create secret tls main-tls --key="../secrets/SectigoSSL.key" --cert="../secrets/SectigoSSL.crt"

kubectl create secret generic flask-conf --from-file=../message-board/conf.cfg

bash ingress.sh

kubectl apply -f deployment-mb.yaml

kubectl apply -f deployment-docs.yaml

echo "Waiting 60s before appling ingress"
sleep 60
kubectl apply -f ingress.yaml
