FROM python:slim-bullseye
WORKDIR /messageBoard
COPY . .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
CMD ["gunicorn", "app:app", "-w", "2", "--threads", "2", "--bind", ":5000"]

