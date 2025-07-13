import csv
import json
from pathlib import Path
import requests


def log_missing(isbn, reason, log_file_path):
    entry = (isbn, str(reason))

    # Check if the entry already exists
    if Path(log_file_path).exists():
        with open(log_file_path, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            for row in rows:
                if len(row) >= 2 and (row[0], row[1]) == entry:
                    return  # Already logged

    # Log new entry
    with open(log_file_path, "a", newline="") as f:
        writer = csv.writer(f)
        if len(rows) == 0:
            writer.writerow(["isbn", "reason"])
        writer.writerow(entry)


def get_book_metadata(isbn):
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    return response.json()


def get_thumbnail_url(volume_info):
    image_links = volume_info.get("imageLinks", {})
    thumbnail_url = image_links.get("thumbnail")
    if thumbnail_url:
        thumbnail_url = thumbnail_url.replace("http://", "https://")
        thumbnail_url += "&fife=w200"
    return thumbnail_url


def download_thumbnail(url, output_path):
    response = requests.get(url, timeout=10)
    if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
        with open(output_path, "wb") as f:
            f.write(response.content)
        return True
    return False


def fetch_google_books_thumbnail(isbn, output_path, log_file):
    try:
        data = get_book_metadata(isbn)
        items = data.get("items", [])
        if not items:
            log_missing(isbn, "no book found", log_file)
            print(f"> No book found for ISBN {isbn}")
            return

        volume_info = items[0].get("volumeInfo", {})
        thumbnail_url = get_thumbnail_url(volume_info)

        if not thumbnail_url:
            log_missing(isbn, "no thumbnail", log_file)
            print(f"> No thumbnail for ISBN {isbn}")
            return

        success = download_thumbnail(thumbnail_url, output_path)
        if success:
            print(f"> Downloaded cover for ISBN {isbn}")
        else:
            log_missing(isbn, "image download failed", log_file)
            print(f"> Failed to download image for ISBN {isbn}")

    except Exception as e:
        log_missing(isbn, str(e), log_file)
        print(f"> Error for ISBN {isbn}: {e}")


if __name__ == "__main__":

    data_dir = Path("data/books")

    output_dir = Path("assets/book-covers")
    output_dir.mkdir(parents=True, exist_ok=True)

    log_file = Path("assets/book-covers-missing.csv")
    log_file.touch(exist_ok=True)

    for json_file in data_dir.glob("*.json"):
        region_name = json_file.stem
        region_folder = output_dir / region_name
        region_folder.mkdir(parents=True, exist_ok=True)

        with open(json_file, "r", encoding="utf-8") as f:
            region_data = json.load(f)

        for country, books in region_data.items():
            for book in books:
                isbn = book.get("isbn")
                if not isbn:
                    continue

                output_path = region_folder / f"{isbn}.jpg"
                if output_path.exists():
                    continue

                fetch_google_books_thumbnail(isbn, output_path, log_file)
