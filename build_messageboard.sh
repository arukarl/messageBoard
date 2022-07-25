kops export kubecfg --admin

cd message-board || true

docker build -t karlaru/message-board .

docker login

docker push karlaru/message-board:latest

# Copy static files to S3 and set browser cache control
aws s3 cp static/ s3://karlaru-mb/static/ --cache-control max-age=2592000 --recursive

# Flask conf file is mounted to container as secret
kubectl delete secret flask-conf

kubectl create secret generic flask-conf --from-file=../secrets/conf.cfg

kubectl rollout restart deployment/mb

# Formulas to calc hashes for script and css files. Manually enter to HTML files....
# shasum -b -a 384 static/form-script.js | awk '{ print $1 }' | xxd -r -p | base64
# shasum -b -a 384 static/back.js | awk '{ print $1 }' | xxd -r -p | base64
# shasum -b -a 384 static/custom.css | awk '{ print $1 }' | xxd -r -p | base64
# shasum -b -a 384 static/thumbnail.js | awk '{ print $1 }' | xxd -r -p | base64
