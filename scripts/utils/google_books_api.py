import logging
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


BASE_URL = "https://www.googleapis.com/books/v1/volumes"


def get_book_metadata(isbn):
    response = requests.get(BASE_URL, params={"q": f"isbn:{isbn}"}, timeout=10)
    response.raise_for_status()
    return response.json()


def get_thumbnail_url(book_data):
    volume_info = book_data.get("volumeInfo", {})
    image_links = volume_info.get("imageLinks", {})
    thumbnail_url = image_links.get("thumbnail")
    if thumbnail_url:
        thumbnail_url = thumbnail_url.replace("http://", "https://")
        thumbnail_url += "&fife=w200"
    return thumbnail_url


def download_thumbnail(url, thumbnail_path):
    response = requests.get(url, timeout=10)
    content_type = response.headers.get("Content-Type", "")
    if "image" not in content_type:
        raise ValueError(
            f"Invalid content type: expected image but got '{content_type}'"
        )

    with open(thumbnail_path, "wb") as file:
        file.write(response.content)


def fetch_google_books_thumbnail(isbn, thumbnail_path):
    try:
        data = get_book_metadata(isbn)
        items = data.get("items", [])
        if not items:
            logger.error("%s - No book found", isbn)
            return

        thumbnail_url = get_thumbnail_url(items[0])

        if not thumbnail_url:
            logger.error("%s - No thumbnail", isbn)
            return

        download_thumbnail(thumbnail_url, thumbnail_path)

    except RequestException as e:
        logger.error("%s - Request failed: %s", isbn, e)
    except ValueError as e:
        logger.error("%s - %s", isbn, e)
