import logging
from datetime import datetime
from os import environ
from sys import exit, stdout

import dotenv
from discord_webhook import DiscordEmbed, DiscordWebhook
from loguru import logger
from loguru_discord import DiscordSink

from handlers.intercept import Intercept
from services.ipapi import FetchIP


def Start() -> None:
    """Initialize Callsign and begin primary functionality."""

    logger.info("Callsign")
    logger.info("https://github.com/EthanC/Callsign")

    # Reroute standard logging to Loguru
    logging.basicConfig(handlers=[Intercept()], level=0, force=True)

    if dotenv.load_dotenv():
        logger.success("Loaded environment variables")
        logger.trace(environ)

    if level := environ.get("LOG_LEVEL"):
        logger.remove()
        logger.add(stdout, level=level)

        logger.success(f"Set console logging level to {level}")

    if url := environ.get("LOG_DISCORD_WEBHOOK_URL"):
        logger.add(
            DiscordSink(url),
            level=environ["LOG_DISCORD_WEBHOOK_LEVEL"],
            backtrace=False,
        )

        logger.success(f"Enabled logging to Discord webhook")
        logger.trace(url)

    data: dict[str, str | bool | float] | None = FetchIP()

    if not data:
        logger.debug("Exiting, no IP address data to parse")

        return

    changed: bool = Checkpoint(data)

    if not changed:
        logger.info("Latest IP address matches the last known IP address")

        return

    Notify(data)


def Checkpoint(data: dict[str, str | bool | float]) -> bool:
    """
    Return a boolean value indicating whether or not the IP address has
    changed based on a comparison between the local file checkpoint.txt
    and the latest data passed to the function.
    """

    local: str | None = None
    latest: str | None = None

    try:
        with open("checkpoint.txt", "r") as file:
            local = file.read()
    except Exception as e:
        # Log this Exception as debug because it's likely due to the
        # local file not existing, which is valid.
        logger.opt(exception=e).debug("Failed to read file checkpoint.txt")

    try:
        latest = str(data["ip"])
    except Exception as e:
        logger.opt(exception=e).error("Failed to parse latest IP address")

        # If we don't have the latest IP address to compare to, something
        # is wrong and we should not continue.
        return False

    # At this point, we have both local and latest set to their intended
    # values, so we write latest to the local file before continuing.
    with open("checkpoint.txt", "w+") as file:
        file.write(latest)

    if environ.get("DEBUG"):
        logger.info("DEBUG is enabled in environment variables")

        return True

    if (local == latest) and (not environ.get("DEBUG")):
        logger.debug(f"local {local} == latest {latest}")

        return False

    return True


def Notify(data: dict[str, str | bool | float]) -> None:
    """Report IP address changes to the configured Discord webhook."""

    if not (url := environ.get("DISCORD_WEBHOOK_URL")):
        logger.info("Discord webhook for notifications is not set")

        return

    embed: DiscordEmbed = DiscordEmbed()

    embed.set_color("00C6A8")
    embed.set_author(
        "Callsign",
        url="https://github.com/EthanC/Callsign",
        icon_url="https://i.imgur.com/NgVYZcq.png",
    )

    ip: str = str(data.get("ip", "0.0.0.0"))
    ver: str = str(data.get("version", "IP"))

    embed.add_embed_field(f"{ver} Address", f"[{ip}](https://ipapi.co/?q={ip})")

    if not environ.get("SIMPLE_MODE", False):
        asn: str = str(data.get("asn", "Unknown"))
        city: str = str(data.get("city", "Unknown"))
        region: str = str(data.get("region_code", "Unknown"))
        country: str = str(data.get("country_name", "Unknown"))
        lat: str = str(data.get("latitude", 0))
        lng: str = str(data.get("longitude", 0))

        embed.add_embed_field(
            "ASN", f"[{asn}](https://radar.cloudflare.com/routing/{asn})"
        )
        embed.add_embed_field("Organization", str(data["org"]))

        embed.add_embed_field("Location", f"{city}, {region}")
        embed.add_embed_field("Country", country)
        embed.add_embed_field(
            "Coordinates", f"[{lat}, {lng}](https://maps.google.com/?q={lat},{lng})"
        )

    embed.set_footer("ipapi", icon_url="https://i.imgur.com/54fjVje.png")  # pyright: ignore [reportUnknownMemberType]
    embed.set_timestamp(datetime.now().timestamp())

    DiscordWebhook(url, embeds=[embed], rate_limit_retry=True).execute()


if __name__ == "__main__":
    try:
        Start()
    except KeyboardInterrupt:
        exit()
