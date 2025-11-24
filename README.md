# discord-bot-test

## Deploying
```bash
cp .env.example .env
# Modify the values in .env as needed
vim .env
docker compose up -d
```

## Dev Dependencies
```bash
sudo apt-get install -y libmariadb-dev
python3 -m venv venv
./venv/bin/activate
pip3 install -r requirements.txt
```