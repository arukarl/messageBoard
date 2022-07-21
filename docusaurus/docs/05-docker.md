---
sidebar_position: 5
---

# Docker

messageBoard Flask web application is built into Docker image.

### Gunicorn

Flask doesn't come with production grade WSGI HTTP server out of the box, so 
**[Gunicorn](https://gunicorn.org)** is chosen as the production grade HTTP server.

### Dockerfile

Dockerfile itself is quite straight forward:

```shell title="Dockerfile"
FROM python:slim-bullseye
WORKDIR /messageBoard
COPY . .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
CMD ["gunicorn", "app:app", "--workers", "2", "--threads", "2", "--bind", ":5000"]

```

It is recommended to use at least as many workers as there are CPU cores.
(At the moment there is only 1 worker node in use with 2 core CPU.)  

**Gunicorn** parameters:
- ` --workers 2 ` - 2 workers (1 per CPU core)
- ` --threads 2 ` - 2 threads per worker (total 2 * 2 = 4 threads)
- ` --bind :5000 ` - server socket to bind


