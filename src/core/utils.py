import requests

from logger import logger


def request_page(username: str, page_number: int) -> str:
    url = f"https://{username}.skyrock.com/{page_number}.html"
    logger.debug(f"Requesting page {url}")
    response = requests.get(url)
    return response.text
