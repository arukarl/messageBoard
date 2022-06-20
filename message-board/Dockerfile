FROM python:slim-bullseye
WORKDIR /messageBoard
COPY .. .
RUN pip3 install -r requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD [ "flask", "run"]
