# firestorm-discord-bot

A bot for allowing users on a discord server to suggest prompts for the Bingo Dataset.

## Deploying

### Pre-requisites
- One of the commands implemented by this discord bot, `/sync-dataset`, requires a Github account that has forked the firestorm-bingo repository.
    - Ensure that the Github user that you intend to use in the `.env` file has forked the repo before deploying.

### Running the bot

```bash
cp .env.example .env
# Modify the values in .env as needed
vim .env
docker compose up -d
```

## Development
### Dependencies (If running without Docker)
```bash
sudo apt-get install -y libmariadb-dev
python3 -m venv venv
./venv/bin/activate
pip3 install -r requirements.txt
```

### Running with Docker
- Same instructions as the deployment

### Running without Docker
```bash
python3 -m app.main
```

### Running unittests
```bash
nose2
```

## Misc. Scripts
### Porting a JSON dataset to the Database
To port an existing JSON dataset to the database, run the following:

```bash
cp scripts/.env.example scripts/.env
# Fill up the .env information with your DB connection details
vim scripts/.env
python3 scripts/json_to_db.py path_to_json_dataset.json
```