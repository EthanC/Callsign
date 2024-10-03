import httpx
from httpx import Response
from loguru import logger


def FetchIP() -> dict[str, str | bool | float] | None:
    """
    Fetch the IP address JSON response object for the current client
    from the ipapi.co API.
    """

    logger.debug("GET https://ipapi.co/json")

    try:
        res: Response = httpx.get(
            "https://ipapi.co/json",
            headers={"User-Agent": "https://github.com/EthanC/Callsign"},
        )

        res.raise_for_status()
        logger.trace(res.text)

        return res.json()
    except Exception as e:
        logger.opt(exception=e).error("Failed to fetch IP address from ipapi")
