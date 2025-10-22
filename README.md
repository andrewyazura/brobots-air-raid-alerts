[![Stand With Ukraine](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-direct-single.svg)](https://stand-with-ukraine.pp.ua)

# Brobots Air Raid Alerts

Tell students whether to go to school. 
Every day in the morning in checks air raid alert
status and sends a message to subscribed users and channels.

Information source: https://t.me/air_alert_ua

## Deployment

1. Add the project to your flake inputs

```nix
inputs = {
    brobots-alerts-app = { url = "github:andrewyazura/brobots-air-raid-alerts"; };
};
```

2. Import the nixos module

```nix
imports = [ inputs.brobots-alerts-app.nixosModules.default ];
```

3. Enable the service

```nix
services.brobots-alerts = {
    enable = true;
    environmentFile = /path/to/env/file;
};
```

## Setting up the database

1. `CREATE USER alerts_app WITH ENCRYPTED PASSWORD 'pass1234';`
2. `CREATE DATABASE air_raid_alerts;`
3. `\c air_raid_alerts`
4. `GRANT ALL PRIVILEGES ON DATABASE air_raid_alerts TO alerts_app;`
5. `GRANT ALL ON schema public TO alerts_app;`
