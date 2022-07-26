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



# Upload Lambda Functions as zip files to s3
aws s3 cp . s3://mb-conf-folder/ --recursive --exclude "*" --include "*.zip"

# Build cleanup
rm *.zip
rm -r lambda_img_scaler/python

cd ..

aws s3 cp secrets/ s3://mb-conf-folder/ --recursive

aws cloudformation create-stack --stack-name messageBoard \
                                  --template-body file://cloud-formation/base_stack.yaml \
                                  --capabilities CAPABILITY_IAM \
                                  --output yaml
