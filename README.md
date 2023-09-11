[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Brobots Air Raid Alerts

Tell students whether to go to school. 
Every day in the morning in checks air raid alert
status and sends a message to subscribed users and channels.

Information source: https://t.me/air_alert_ua

## Deployment

1. Pull project image from this repo's packages
2. Add `.env` file with your settings
3. Start the container

## Setting up the database

1. `CREATE USER alerts_app WITH ENCRYPTED PASSWORD 'pass1234';`
2. `CREATE DATABASE air_raid_alerts;`
3. `\c air_raid_alerts`
4. `GRANT ALL PRIVILEGES ON DATABASE air_raid_alerts TO alerts_app;`
5. `GRANT ALL ON schema public TO alerts_app;`
