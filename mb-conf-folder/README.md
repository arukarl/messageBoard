## Files that will be uploaded to config s3 bucket

### For NGINX
- SSL cert (not in Version Control)
- SSL key (not in Version Control)
- Diffie-Hellman key (not in Version Control)
- nginx repo
- nginx conf


### For EC2 instance
- install nginx and docker


### For Lambda functions
Zip files of lambda functions that [build_webapp.sh](../build_messageboard.sh) script will create locally before uploading files to s3 bucket.
- Create thumbnail (scale) function zip file
- Pillow library layer for image scaler function
- Update DynamoDB img url to thumbnail url
- Delete image