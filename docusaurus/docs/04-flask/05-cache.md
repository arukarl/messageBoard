---
sidebar_position: 5
---

# Flask-Caching

### Overview

**[Flask-Caching](https://github.com/pallets-eco/flask-caching)** is an extension to Flask 
that adds caching support for various backends to any Flask application.

Cache is used to reduce the number of database calls. There are 2 caches - one for users and the other for messages.

### User table cache

[Flask-Login](/flask/flask-login) loads user object `@login_manager.user_loader` each time when
`@login_required` annotated app route is requested. 
`load_user(user_id)` function gets user information from **users database** by `user_id`. 
So without cache **users database** would get a huge number of requests.

Solution to this problem is caching `load_user(user_id)` function. 
When Flask-Login loads user (with User object creation), the returned `User` object is cached in local python dictionary.
On next call to `load_user(user_id)` cached `User` object is returned, if function parameter `user_id` is the same.
When logging out this cached object for the current user is deleted.

### Messages table cache

Since `messages` DB is quite lightweight and can fit to the VM memory, all entries (tuples) of the DB are stored in
memory cache after call to `get_all_messages` function. 
Local cache is invalidated when message is added or deleted from DB. Cache timeout is quite small, because when
there are multiple containers running, cache invalidations are not synchronized between containers. 
Query to DB every 5 seconds should give acceptable user experience. 
(Changes in the same container will be instant and max 5 seconds delay to others)

### Python code

```python title="app.py"
...
from flask_caching import Cache
...

cache = Cache(app)
user_object_cache_timeout = 600   # seconds
messages_table_cache_timeout = 5  # seconds

@cache.memoize(timeout=messages_table_cache_timeout)
def get_all_messages():
    """ Read all messages from AWS DynamoDB and cache method return value """
    messages = messages_table.scan()['Items']
    messages = map(set_images_url, messages)
    return sorted(messages, key=lambda m: m['timestamp'], reverse=True)
    
...

@login_manager.user_loader
@cache.memoize(timeout=user_object_cache_timeout)
def load_user(user_id):
    """ Load user from DynamoDB by user_id and return cached User object """
    user = get_dynamodb_user(user_id)
    return User(user['username'], user['id'])
    
    
class User:
    """ Flask-Login User class """
    def __init__(self, name, id, active=True):
        ...
...

@app.route("/logout", methods=['GET'])
@login_required
def logout():
    """ Logout user """
    cache.delete_memoized(load_user, current_user.id)
    logout_user()
    return redirect("/")
    
...

@app.route("/save", methods=['POST'])
@login_required
def post_message():
    ...
    cache.delete_memoized(get_all_messages)
    ...
    
...
@app.route("/delete", methods=['POST'])
@login_required
def delete():
    ...
    cache.delete_memoized(get_all_messages)
    ...

```


