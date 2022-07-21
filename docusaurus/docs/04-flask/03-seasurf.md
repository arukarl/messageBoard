---
sidebar_position: 3
---

# Flask-SeaSurf


### Overview

**[SeaSurf](https://github.com/maxcountryman/flask-seasurf)** is a Flask extension for preventing cross-site request forgery (CSRF).
This is used in when posting and deleting messages.

### Security

Changes in default config:

```python title="conf.cfg"
...
CSRF_COOKIE_SECURE='True'
CSRF_COOKIE_HTTPONLY='True'
...
```

### Usage in templates

Code below is added to the templates where **POST** HTTP methods are used.
These requests are validated against the CSRF token sent by the client and as rendered on the page.

```html 
<input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">
```

:::tip
Only exception is Google login `login_auth()` function, which is `@csrf.exempt`, 
because Google csrf token is used instead of SeaSurf.
:::

### Python code

Code is really simple.

```python title="app.py"
...
from flask_seasurf import SeaSurf
...
csrf = SeaSurf(app)
...
```
