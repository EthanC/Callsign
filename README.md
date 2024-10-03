# Callsign

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/EthanC/Callsign/ci.yaml?branch=main) ![Docker Pulls](https://img.shields.io/docker/pulls/ethanchrisp/callsign?label=Docker%20Pulls) ![Docker Image Size (tag)](https://img.shields.io/docker/image-size/ethanchrisp/callsign/latest?label=Docker%20Image%20Size)

Callsign monitors your public IP address and notifies when it changes.

<p align="center">
    <img src="https://i.imgur.com/zoszsfp.png" draggable="false">
</p>

## Setup

A [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) is recommended for notifications.

Regardless of your chosen setup method, Callsign is intended for use with a task scheduler, such as [cron](https://crontab.guru/).

**Environment Variables:**

-   `LOG_LEVEL`: [Loguru](https://loguru.readthedocs.io/en/stable/api/logger.html) severity level to write to the console.
-   `LOG_DISCORD_WEBHOOK_URL`: [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) URL to receive log events.
-   `LOG_DISCORD_WEBHOOK_LEVEL`: Minimum [Loguru](https://loguru.readthedocs.io/en/stable/api/logger.html) severity level to forward to Discord.
-   `DISCORD_WEBHOOK_URL`: [Discord Webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks) URL to receive IP address change notifications.
-   `SIMPLE_MODE`: Omit all extra information from the Discord embed notification other than the IP address. Optional, default False.

### Docker (Recommended)

Modify the following `compose.yaml` example file, then run `docker compose up`.

```yaml
services:
  callsign:
    container_name: callsign
    image: ethanchrisp/callsign:latest
    environment:
      LOG_LEVEL: INFO
      LOG_DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/YYYYYYYY/YYYYYYYY
      LOG_DISCORD_WEBHOOK_LEVEL: WARNING
      DISCORD_WEBHOOK_URL: https://discord.com/api/webhooks/XXXXXXXX/XXXXXXXX
```

### Standalone

Callsign is built for [Python 3.12](https://www.python.org/) or greater.

1. Install required dependencies using [uv](https://github.com/astral-sh/uv): `uv sync`
2. Rename `.env_example` to `.env`, then provide the environment variables.
3. Start Callsign: `python callsign.py`
