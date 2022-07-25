kops export kubecfg --admin

cd docusaurus|| true

npm run build

docker build -t karlaru/mbdocs .

docker login

docker push karlaru/mbdocs:latest

kubectl rollout restart deployment/docs
