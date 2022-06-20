# Creating thumbnail function
zip -r -j  mb-conf-folder/img_scaler.zip lambda_img_scaler/img_scaler.py

# Creating Pillow layer library
cd lambda_img_scaler/
pip install --target ./python Pillow
zip -r pillow_layer.zip python
cd ..
mv lambda_img_scaler/pillow_layer.zip mb-conf-folder/pillow_layer.zip

# Full size image url to thumbnail url
zip -r -j  mb-conf-folder/dynamo_img_update.zip lambda_dynamo_img_update/dynamo_img_update.py

# Delete pictures
zip -r -j  mb-conf-folder/img_delete.zip lambda_img_delete/img_delete.py

# Create docker image
docker build -t karlaru/message-board .

# DockerHub login
docker login

# Push image to DockerHub
docker push karlaru/message-board:latest

# Copy style file to S3 and set browser cache control
aws s3 cp static/style_min.css s3://karlaru-mb/static/ --cache-control max-age=2592000 --acl public-read

# Copy other conf and TLS (SSL) files to S3
aws s3 cp mb-conf-folder s3://mb-conf-folder/ --recursive

# Delete temp *.zip files
rm mb-conf-folder/*.zip

# If stack doesn't already exist - create new
if ! aws cloudformation describe-stacks --stack-name messageboard ; then

  echo "Creating new stack!"

  aws cloudformation create-stack --stack-name messageboard \
                                  --template-body file://aws_stack.yaml \
                                  --capabilities CAPABILITY_IAM

# If stack already exists - update
else

  echo "Updating existing stack!"

  aws cloudformation update-stack --stack-name messageboard \
                                  --template-body file://aws_stack.yaml \
                                  --capabilities CAPABILITY_IAM

fi

