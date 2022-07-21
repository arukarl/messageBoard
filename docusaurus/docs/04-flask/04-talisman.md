---
sidebar_position: 4
---

# Flask-Talisman

### Overview

**[Talisman](https://github.com/GoogleCloudPlatform/flask-talisman)** is a small Flask extension that handles setting 
HTTP headers that can help protect against a few common web application security issues.

### Security

**Changes in default configuration:**

###### Force HTTPS

`force_https=False`

Force https is not needed since Flask app is running behind NGINX server with does TLS termination. 

###### Content Security Policy

Since many sources deliver multiple type of content, it made sense to include them under wildcard `default-src`.
```python
content_security_policy={
    'default-src': [
        'accounts.google.com',              # Google Sign-In
        'd3jwmvy177h8cq.cloudfront.net',    # CloudFront CDN (images and static files)
        'www.gstatic.com',                  # Google reCaptcha
        'fonts.gstatic.com',                # Google fonts
        'cdn.jsdelivr.net/npm/',            # Bootstrap CSS
        'www.google.com'                    # Google reCaptcha
    ]
}
```
:::tip Secure

These are only locations that browser allows to download and run website content from (images, styles and scripts)!

:::

### Python code

```python title="app.py"
...
from flask_talisman import Talisman
...
Talisman(app,
         force_https=False,
         content_security_policy={
             'default-src': [
                 'accounts.google.com',  # Google Sign-In
                 'd3jwmvy177h8cq.cloudfront.net',  # CloudFront CDN (images and static files)
                 'www.gstatic.com',  # Google reCaptcha
                 'fonts.gstatic.com',  # Google fonts
                 'cdn.jsdelivr.net/npm/bootstrap@5.2.0-beta1/',  # Bootstrap CSS
                 'www.google.com'  # Google reCaptcha
             ]
         })
...
```


