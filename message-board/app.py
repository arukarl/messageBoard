import uuid
import boto3
import mimetypes
import re
from botocore.exceptions import ClientError
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash
from flask_caching import Cache
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_recaptcha import ReCaptcha
from flask_seasurf import SeaSurf
from flask_talisman import Talisman
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
app.config.from_pyfile("conf.cfg")

# Cache
cache = Cache(app)
user_object_cache_timeout = 600   # seconds
messages_table_cache_timeout = 5  # seconds

# Security
csrf = SeaSurf(app)
Talisman(app,
         force_https=False,
         content_security_policy={
             'default-src': [
                 'accounts.google.com',  # Google Sign-In
                 'd3jwmvy177h8cq.cloudfront.net',  # CloudFront CDN (images and static files)
                 'www.gstatic.com',  # Google reCaptcha
                 'fonts.gstatic.com',  # Google fonts
                 'cdn.jsdelivr.net/npm/',  # Bootstrap CSS
                 'www.google.com'  # Google reCaptcha
             ]
         })

# Flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"

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
    """ Remove all HTML elements from string """
    return regex.sub('', string)


def set_images_url(message, cdn_url=cdn_url):
    """ Add images CDN URLs to message object """
    message['thumbnail_url'] = cdn_url + "thumbnails/" + message['img']
    message['img_url'] = cdn_url + "images/" + message['img']
    return message


@cache.memoize(timeout=messages_table_cache_timeout)
def get_all_messages():
    """ Read all messages from AWS DynamoDB and cache method return value """
    try:
        messages = messages_table.scan()['Items']
    except ClientError as err:
        flash(f"Couldn't query messages table. Here's why: {err.response['Error']['Message']}")
        return []

    messages = map(set_images_url, messages)
    return sorted(messages, key=lambda m: m['timestamp'], reverse=True)


def put_dynamodb_messages(message_id, s3_name, author, location, description):
    """ Write new message to AWS DynamoDB """
    try:
        messages_table.put_item(Item={
            "message_id": message_id,
            "img": s3_name,
            "timestamp": str(datetime.now()),
            "author": author,
            "location": location,
            "description": description,
            "google_id": current_user.id
        })
    except ClientError as err:
        flash(f"Couldn't put message to a table. Here's why: {err.response['Error']['Message']}")


def get_dynamodb_user(user_id):
    """ Get current user from db """
    item = []
    try:
        item = user_table.get_item(Key={'id': user_id})['Item']
    except ClientError as err:
        flash(f"Couldn't query users table. Here's why: {err.response['Error']['Message']}")
    except KeyError:
        flash(f"User with id {user_id} not found from users table")
    return item


@login_manager.user_loader
@cache.memoize(timeout=user_object_cache_timeout)
def load_user(user_id):
    """ Load user from DynamoDB by user_id and return cached User object """
    user = get_dynamodb_user(user_id)
    if user:
        return User(user['username'], user['id'])
    else:
        flash("Coudn't load User Object")


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
    messages = get_all_messages()
    return render_template('home.html', messages=messages)


@app.route("/login", methods=['GET'])
def login_page():
    """ Login page """
    return render_template('login.html')


@csrf.exempt
@app.route("/auth", methods=['POST'])
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
        user_id = id_info['sub']
        username = id_info['name']
    except ValueError:
        flash('Invalid Google ID token')
        return login_page()
    try:
        user_table.put_item(Item={"id": user_id, "username": username})
    except ClientError as err:
        flash(f"Couldn't put item to users table. Here's why: {err.response['Error']['Message']}")

    login_user(User(username, user_id))

    return redirect("/my")


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """ Logout user """
    cache.delete_memoized(load_user, current_user.id)
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
        content_type = mimetypes.guess_type(img_file.filename)[0]
        img_format = img_file.filename.split('.')[-1].lower()

        if img_format not in accepted_image_types:
            flash("Invalid photo type")
            flash("Accepted only " + ', '.join(accepted_image_types))
            return redirect(f"/post?author={new_author}&location={new_location}&description={new_message}")

        message_id = str(uuid.uuid4())
        img_s3_name = str(uuid.uuid4()) + '.' + img_format

        try:
            s3_client.upload_fileobj(img_file, s3_bucket, 'images/' + img_s3_name,
                                     ExtraArgs={'CacheControl': 'max-age=86400, public',
                                                'ContentType': content_type})
        except ClientError as err:
            flash(f"Couldn't upload image to s3 bucket. Here's why: {err.response['Error']['Message']}")

        put_dynamodb_messages(message_id, img_s3_name, new_author, new_location, new_message)
        flash("Message stored! Generating thumbnail....")
        cache.delete_memoized(get_all_messages)
    else:
        flash('Invalid reCAPTCHA!')
        return redirect(f"/post?author={new_author}&location={new_location}&description={new_message}")
    return redirect('/my')


@app.route("/my", methods=['GET'])
@login_required
def my_messages():
    """ Signed in page showing users' messages """
    messages = filter(lambda message: message['google_id'] == current_user.id, get_all_messages())

    return render_template('my_images.html', messages=messages)


@app.route("/delete", methods=['POST'])
@login_required
def delete():
    """ Delete message """
    message_id = request.form["id"]
    google_id = request.form["google_id"]
    if message_id and google_id == current_user.id:
        try:
            messages_table.delete_item(Key={"message_id": message_id})
        except ClientError as err:
            flash(f"Couldn't delete message from table. Here's why: {err.response['Error']['Message']}")
        except KeyError:
            flash("Message not found!")

        cache.delete_memoized(get_all_messages)
    else:
        flash("Permission denied")
    return redirect('/my')


@app.route("/acc", methods=['GET'])
@login_required
def my_account():
    """ Account information """
    return render_template('my_account.html')


@app.route("/image/<image_name>", methods=['GET'])
def image(image_name):
    """ Image analysis """
    messages = filter(lambda message: message['img'] == image_name, get_all_messages())
    if not messages:
        flash("Image not found")
    return render_template('image.html', messages=messages)


if __name__ == '__main__':
    app.run()
