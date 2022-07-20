import uuid
import boto3
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_recaptcha import ReCaptcha
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from boto3.dynamodb.conditions import Key

from flask_seasurf import SeaSurf
from flask_talisman import Talisman

app = Flask(__name__)
app.config.from_pyfile("conf.cfg")

# Security
csrf = SeaSurf(app)
Talisman(app,
         force_https=False,
         content_security_policy={
             'default-src': [
                 'accounts.google.com',  # Google Sign-In
                 'd3jwmvy177h8cq.cloudfront.net',  # CloudFront CDN
                 'www.gstatic.com',  # Google reCaptcha
                 'fonts.gstatic.com',  # Google fonts
                 'cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/',  # Bootstrap CSS
                 'www.google.com'  # Google reCaptcha
             ]
         })

# Flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

# AWS config
aws_region = "eu-north-1"
s3_bucket = "karlaru-mb"
cdn_url = "https://d3jwmvy177h8cq.cloudfront.net/"

# AWS resources (state)
s3_client = boto3.client('s3', region_name=aws_region)
dynamodb = boto3.resource('dynamodb', region_name=aws_region)
messages_table = dynamodb.Table("messages")
user_table = dynamodb.Table("users")

# Create a ReCaptcha object
recaptcha = ReCaptcha(app)

# Allowed img types
accepted_image_types = ['jpg', 'jpeg', 'bmp', 'gif', 'png']

# Sanitize form input
regex = re.compile(r'<[^>]+>')


def remove_html(string):
    return regex.sub('', string)


def upload_s3(img_path, s3_name, message_id):
    """ Upload image file with given random name to s3 bucket """
    s3_client.upload_fileobj(img_path, s3_bucket, 'images/' + s3_name,
                             ExtraArgs={'CacheControl': 'max-age=86400, public',
                                        'Metadata': {'message_id': message_id}})


def img_url(message):
    message['img_url'] = cdn_url + "thumbnails/" + message['img']
    return message


def get_dynamodb():
    """ Read all messages from AWS DynamoDB """

    messages = messages_table.scan(FilterExpression=Key('thumbnail').eq("true"))['Items']
    messages = map(img_url, messages)
    return sorted(messages, key=lambda m: m['timestamp'], reverse=True)


def put_dynamodb(message_id, s3_name, author, location, description):
    """ Write new message to AWS DynamoDB """

    messages_table.put_item(Item={
        "message_id": message_id,
        "img": s3_name,
        "timestamp": str(datetime.now()),
        "author": author,
        "location": location,
        "description": description,
        "google_id": current_user.id,
        "thumbnail": "false"
    })


@login_manager.user_loader
def load_user(user_id):
    """ Load user from DynamoDB by user_id """
    user = user_table.get_item(Key={'id': user_id})['Item']
    return User(user['username'], user['id'])


class User:
    """ Flask-Login User class """

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
    messages = get_dynamodb()
    return render_template('home.html', messages=messages)


@app.route("/login", methods=['GET'])
def login_page():
    """ Login page """
    return render_template('login.html')


@csrf.exempt
@app.route("/login", methods=['POST'])
def login_auth():
    """ Verify Google user, create User object and put user data to DynamoDB """

    # Verify the Cross-Site Request Forgery (CSRF) token
    csrf_token_cookie = request.cookies.get('g_csrf_token')
    if not csrf_token_cookie:
        flash('No CSRF token in Cookie.')
        return login_page()
    csrf_token_body = request.form['g_csrf_token']
    if not csrf_token_body:
        flash('No CSRF token in post body.')
        return login_page()
    if csrf_token_cookie != csrf_token_body:
        flash('Failed to verify double submit cookie.')
        return login_page()

    # Validate Google ID token
    try:
        token = str(request.form['credential'])
        client_id = "672740708731-oudggtkgmcuagh01hfm89jnjvjb94s6r.apps.googleusercontent.com"
        id_info = id_token.verify_oauth2_token(token, requests.Request(), client_id)
        userid = id_info['sub']
        username = id_info['name']
    except ValueError:
        flash('Invalid Google ID token')
        return login_page()

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
    new_author = remove_html(request.form['author'])
    new_location = remove_html(request.form['location'])
    new_message = remove_html(request.form['description'])
    if recaptcha.verify():
        img_file = request.files['img']
        img_format = img_file.filename.split('.')[-1].lower()
        if img_format not in accepted_image_types:
            flash("Invalid photo type")
            flash("Accepted only " + ', '.join(accepted_image_types))
            return redirect(f"/post?author={new_author}&location={new_location}&description={new_message}")

        message_id = str(uuid.uuid4())
        s3_name = str(uuid.uuid4()) + '.' + img_format
        upload_s3(img_file, s3_name, message_id)

        put_dynamodb(message_id, s3_name, new_author, new_location, new_message)
        flash("Message stored")
        flash("Generating thumbnail.... Refresh after few seconds")
    else:
        flash('Invalid reCAPTCHA!')
        return redirect(f"/post?author={new_author}&location={new_location}&description={new_message}")
    return redirect('/my')


@app.route("/my", methods=['GET'])
@login_required
def my_messages():
    """ Signed in page showing users' messages """
    data = get_dynamodb()
    user_messages = filter(lambda message: message['google_id'] == current_user.id, data)
    return render_template('my_images.html', messages=user_messages)


@app.route("/delete", methods=['POST'])
@login_required
def delete():
    """ Delete message """
    message_id = request.form["id"]
    if message_id:
        try:
            messages_table.delete_item(Key={"message_id": message_id})
        except:
            flash("Message is not found")

    return redirect('/my')


@app.route("/acc", methods=['GET'])
@login_required
def my_account():
    """ Account information """
    return render_template('my_account.html')


@app.route("/image/<image_name>", methods=['GET'])
def image(image_name):
    """ Image analysis """

    message = messages_table.scan(FilterExpression=Key('img').eq(image_name))['Items'][0]
    message['img_url'] = cdn_url + "images/" + message['img']
    return render_template('image.html', message=message)


@app.errorhandler(404)
def page_not_found(e):
    """ Redirect all nonexistent URLs to home page"""
    return redirect('/')


if __name__ == '__main__':
    app.run()
