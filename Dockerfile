FROM python:3.12-slim

WORKDIR /app

ADD main.py /app/
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]