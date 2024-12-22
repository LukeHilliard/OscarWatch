import json

with open("/var/www/OscarWatchApp/OscarWatch/.client_secret.json") as config_file:
    config = json.load(config_file)