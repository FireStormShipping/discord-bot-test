FROM python:3.12-slim

RUN apt update && apt install -y --no-install-recommends \
  build-essential libmariadb-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY ./app/ /app/app

ENTRYPOINT ["python3", "-m", "app.main"]
