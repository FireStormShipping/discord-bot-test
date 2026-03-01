FROM python:3.12-slim

WORKDIR /app

ADD ./app/ /app
ADD requirements.txt /app/
RUN apt update && apt install -y build-essential libmariadb-dev
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]
