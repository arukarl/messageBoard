---
sidebar_position: 3
---

# NGINX conf

[Full conf file](https://github.com/KarlAruEE/messageBoard/blob/master/nginx/nginx.conf)

### Main features

##### Upstream

Is used to define groups of servers that can be referenced by proxy_pass.
When multiple servers are available and added to this list, 
by default, requests are distributed between the servers using a weighted round-robin balancing method.

```
   upstream flask_application {
        server         localhost:5000 max_fails=3  fail_timeout=120s;
    }
```

##### Server

Listens only to port 443 (SSL) requests and redirects them to `flask_application` = `localhost:5000` endpoint.
Client (webapp user) max upload size is 50MB (effectively max image size).

```
    server {
        ...
        listen       443 ssl http2;
        server_name  nginx.karlaru.com;
        ...

        client_max_body_size 50M;
        ....
        location / {
            proxy_pass http://flask_application;
      }
```

##### TLS 

SSL configurations to achieve **A+** level with [**SSL Labs**](https://www.ssllabs.com/).
```
    server {
        ....
        ssl_certificate /etc/ssl/certs/SectigoSSL.crt;
        ssl_certificate_key /etc/ssl/private/SectigoSSL.key;
        ssl_dhparam /etc/nginx/dhparam.pem;

        ssl_session_timeout 1d;
        ssl_session_cache shared:MozSSL:10m;
        ssl_session_tickets off;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        add_header Strict-Transport-Security "max-age=63072000" always;

        ssl_stapling on;
        ssl_stapling_verify on;
        ssl_trusted_certificate /etc/ssl/certs/SectigoSSL.crt;
        ...
```
