cd message-board || exit

# Creating thumbnail
zip -r -j  img_scaler.zip lambda_img_scaler/img_scaler.py

cd lambda_img_scaler/ || exit
pip install --target ./python Pillow
zip -r pillow_layer.zip python
cd ..
mv lambda_img_scaler/pillow_layer.zip pillow_layer.zip

# Full size image url to thumbnail url
zip -r -j  dynamo_img_update.zip lambda_dynamo_img_update/dynamo_img_update.py

# Delete pictures
zip -r -j  img_delete.zip lambda_img_delete/img_delete.py

# Upload files to s3
aws s3 cp . s3://mb-conf-folder/ --recursive --exclude "*" --include "*.zip"

# Try to update lambda functions code if function is already created
aws lambda publish-layer-version --layer-name pillow --zip-file fileb://pillow_layer.zip || true
aws lambda update-function-code --function-name img_scaler --zip-file fileb://img_scaler.zip || true
aws lambda update-function-code --function-name dynamo_img_update --zip-file fileb://dynamo_img_update.zip || true
aws lambda update-function-code --function-name delete-image --zip-file fileb://img_delete.zip || true

# Build cleanup
rm *.zip
rm -r message-board/lambda_img_scaler/python

