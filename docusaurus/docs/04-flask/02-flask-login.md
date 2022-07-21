---
sidebar_position: 2
---

# Flask-Login

### Overview

**[Flask-Login](https://github.com/maxcountryman/flask-login)** provides user session management for Flask.

<img src="/img/flask-login.svg" width="800"/>

### Security

#### Cross-Site Request Forgery

When credentials are submitted to log in endpoint (in my case /login with POST method), 
Google uses **double-submit-cookie pattern** to prevent CSRF attacks. 
Before each submission they generate a token. Then this token is put into both
the cookie and the post body, so `csrf_token_cookie == csrf_token_body`.

#### Verify ID token

Google API Client Library is used to validate token. 
The `verify_oauth2_token` function verifies the tokens' JWT signature.

#### @login_required

If user is not logged in, routes with `@login_required` redirect user to `/login` page. 

#### @login_manager.user_loader

This callback is used to reload the user object from the user ID stored in the session.

:::tip
`user_id == google_user_id` in this app, which was received with Google Identity id_token.
:::

### Python code

Relevant Python code extracted from Flask `app.py`.

```python title="app.py"
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Flask login config
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"

user_table = dynamodb.Table("users")

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

    return redirect("/my")


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """ Logout user """
    logout_user()
    ...
    

@app.route("/my", methods=['GET'])
@login_required
def my_messages():
    ...

```


