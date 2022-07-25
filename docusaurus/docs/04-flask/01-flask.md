---
sidebar_position: 1
---

# Flask

### Flask overview

**[Flask](https://github.com/pallets/flask)** is a lightweight WSGI web application framework.

### Templates

There is **base template** called `layout.html`, which defines the HTML skeleton of webapp UI.
**Child templates** fill or overwrite blocks with relevant content for each route.

<img src="/img/flask-templates.svg" width="600"/>

### Functions

Some functions with code snippets from main `app.py` file:

#### Sanitize form input

`remove_html()` function is called on post message form fields: author, location and description. 
Even tho Flask configures Jinja2 to automatically escape all values, all html and other <???> values
are removed to save space. They wouldn't work on site anyway.

```python title="app.py"
import re

# Sanitize form input
regex = re.compile(r'<[^>]+>')


def remove_html(string):
    """ Remove all HTML elements from string """
    return regex.sub('', string)

```

#### Get messages

DynamoDB messages table is scanned with **FilterExpression** to select relevant messages:

| FilterExpression                     | Description                       | Page      | Route               |
|--------------------------------------|-----------------------------------|-----------|---------------------|
| Key('thumbnail').eq("true")          | Get all messages with thumbnails  | Home      | /                   |
| Key('google_id').eq(current_user.id) | Get all current user messages     | My images | /my                 |
| Key('img').eq(image_name)            | Get message with a concrete image | Image     | /image/<image_name> |


Images are stored in database only with **filename** (uuid4).
When there is a need to display them, full URL of images must be found.

:::warning
Images are only accessible via CloudFront.
:::

Dictionary `messages` gets two new values: `thumbnail_url` and `img_url` for full sized image.
Returned messages are sorted newest to oldest.

```python title="app.py"
cdn_url = "https://d3jwmvy177h8cq.cloudfront.net/"

def set_images_url(message):
    """ Add images CDN URLs to message object """
    message['thumbnail_url'] = cdn_url + "thumbnails/" + message['img']
    message['img_url'] = cdn_url + "images/" + message['img']
    return message


@cache.memoize(timeout=messages_table_cache_timeout)
def get_all_messages():
    """ Read all messages from AWS DynamoDB and cache method return value """
    messages = messages_table.scan()['Items']
    messages = map(set_images_url, messages)
    return sorted(messages, key=lambda m: m['timestamp'], reverse=True)
```
