# Brobots Air Raid Alerts

Tell students whether to go to school. 
Every day in the morning in checks air raid alert
status and sends a message to subscribed users and channels.

Information source: https://t.me/air_alert_ua

## Deployment

1. Create a virtual environment with `python3.10`
2. Install dependencies from `Pipfile.lock`
3. Create `.env` file
4. Setup the database
5. Run `main.py`

## Setting up the database

1. `CREATE USER alerts_app WITH ENCRYPTED PASSWORD 'pass1234';`
2. `CREATE DATABASE air_raid_alerts;`
3. `\c air_raid_alerts`
4. `GRANT ALL PRIVILEGES ON DATABASE air_raid_alerts TO alerts_app;`
5. `GRANT ALL ON schema public TO alerts_app;`
