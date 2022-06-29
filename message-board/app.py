import json
import uuid
import boto3
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_recaptcha import ReCaptcha
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'superSecretKey'

# Flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

# AWS config
aws_region = "eu-north-1"
s3_bucket = "karlaru-mb"
cdn_url = "https://d3jwmvy177h8cq.cloudfront.net/"

# AWS resources
s3_client = boto3.client('s3', region_name=aws_region)
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
messages_table = dynamodb.Table("messages")
user_table = dynamodb.Table("users")

# Load secret app config variables from AWS Secrets Manager (for reCAPTCHA)
sm_client = boto3.client('secretsmanager', region_name='eu-north-1')
secrets_string = sm_client.get_secret_value(SecretId="reCAPTCHA")['SecretString']
secrets_dict = json.loads(secrets_string)
for key, value in secrets_dict.items():
    app.config[key] = value

# Create a ReCaptcha object
recaptcha = ReCaptcha(app)

# Allowed img types
accepted_image_types = ['jpg', 'jpeg', 'bmp', 'gif', 'png']


def image_to_s3(img_path, s3_name, message_id):
    """ Upload image file with given random name to s3 bucket """
    s3_client.upload_fileobj(img_path, s3_bucket, 'images/' + s3_name, ExtraArgs={"ACL": "public-read",
                                                                                  "Metadata": {
                                                                                      "message_id": message_id}})


def read_messages_db():
    """ Read all messages from AWS DynamoDB """

    messages = messages_table.scan()['Items']
    return sorted(messages, key=lambda m: m['timestamp'], reverse=True)


def put_dynamodb(message_id, s3_name, author, location, description):
    """ Write new message to AWS DynamoDB """

    messages_table.put_item(Item={
        "message_id": message_id,
        "img": cdn_url + 'images/' + s3_name,
        "timestamp": str(datetime.now()),
        "author": author,
        "location": location,
        "description": description,
        "google_id": current_user.id
    })


@login_manager.user_loader
def load_user(user_id):
    """ Load user from DynamoDB by user_id """
    user = user_table.get_item(Key={'id': user_id})['Item']
    return User(user['username'], user['id'])


class User:
    """ Flask User class """

    def __init__(self, name, id, active=True):
        self.id = id
        self.name = name
        self.is_active = active
        self.is_authenticated = True

    def is_authenticated(self):
        return self.is_authenticated

    def is_active(self):
        return self.is_active

    def get_id(self):
        return self.id


@app.route("/", methods=['GET'])
def home():
    """ Home page, display all messages """
    messages = read_messages_db()
    return render_template('home.html', messages=messages)


@app.route("/login", methods=['GET'])
def log_in():
    """ Login page """
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def login():
    """ Verify Google user, create User object and put user data to DynamoDB """
    token = str(request.form['credential'])
    client_id = "672740708731-oudggtkgmcuagh01hfm89jnjvjb94s6r.apps.googleusercontent.com"
    id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
    userid = id_info['sub']
    username = id_info['name']

    user_table.put_item(Item={"id": userid, "username": username})
    login_user(User(username, userid))

    return redirect("/my-messages")


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """ Logout user """
    if request.args.get("rm") == "true":
        user_table.delete_item(Key={"id": current_user.id})

    logout_user()
    return redirect("/")


@app.route("/post", methods=['GET'])
@login_required
def post():
    """ Image posting form """
    return render_template('post_image.html')


@app.route("/save", methods=['POST'])
@login_required
def post_message():
    """ Upload full size image to S3. Make DynamoDB message entry. """
    new_author = request.form['author']
    new_location = request.form['location']
    new_message = request.form['description']
    if recaptcha.verify():
        img_file = request.files['img']
        img_format = img_file.filename.split('.')[-1].lower()
        if img_format not in accepted_image_types:
            flash("Invalid photo type")
            flash("Accepted only " + ', '.join(accepted_image_types))
            return redirect("/post")

        message_id = str(uuid.uuid4())
        s3_name = str(uuid.uuid4()) + '.' + img_format
        image_to_s3(img_file, s3_name, message_id)

        put_dynamodb(message_id, s3_name, new_author, new_location, new_message)
    else:
        flash('Invalid reCAPTCHA!')
        return redirect("/post")
    return redirect("/my")


@app.route("/my", methods=['GET'])
@login_required
def my_messages():
    """ Signed in page showing users' messages """
    data = read_messages_db()
    user_messages = filter(lambda message: message['google_id'] == current_user.id, data)
    return render_template('my_images.html', messages=user_messages)


@app.route("/delete", methods=['GET'])
@login_required
def delete():
    """ Delete message """
    message_id = request.args.get("id")
    if message_id:
        try:
            img_name = messages_table.get_item(Key={'message_id': message_id})['Item']['img'].split("/")[-1]
            messages_table.delete_item(Key={"message_id": message_id})
            sqs_client = boto3.client('sqs', region_name=aws_region)
            sqs_client.send_message(QueueUrl='https://sqs.eu-north-1.amazonaws.com/978039897892/delete-image',
                                    MessageBody=json.dumps({"image_name": img_name}))
        except:
            flash("Message is already deleted")

    return my_messages()


@app.route("/acc", methods=['GET'])
@login_required
def my_account():
    """ Account information """
    return render_template('my_account.html')


@app.errorhandler(404)
def page_not_found(e):
    """ Redirect all nonexistent URLs to home page"""
    return redirect('/')


if __name__ == '__main__':
    app.run()
