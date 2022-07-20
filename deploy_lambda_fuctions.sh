cd message-board || exit

# Creating thumbnail function
zip -r -j  img_scaler.zip lambda_img_scaler/img_scaler.py

cd lambda_img_scaler/ || exit
pip install --target ./python Pillow
zip -r pillow_layer.zip python
cd ..
mv lambda_img_scaler/pillow_layer.zip pillow_layer.zip

# Delete pictures function
zip -r -j  img_delete.zip lambda_img_delete/img_delete.py

# Upload zip files to s3
aws s3 cp . s3://mb-conf-folder/ --recursive --exclude "*" --include "*.zip"

# Update lambda functions code if function is already created
aws lambda publish-layer-version --layer-name pillow \
                                 --zip-file fileb://pillow_layer.zip \
                                 --output yaml || true

aws lambda update-function-code --function-name img_scaler \
                                --zip-file fileb://img_scaler.zip \
                                --output yaml || true

aws lambda update-function-code --function-name delete-image \
                                --zip-file fileb://img_delete.zip \
                                --output yaml || true

# Build cleanup
rm *.zip
rm -r lambda_img_scaler/python
