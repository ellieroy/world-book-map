import json
from pathlib import Path
from tqdm import tqdm
from utils.google_books_api import fetch_google_books_thumbnail
from utils.logging import setup_logging


BOOK_DATA_JSON = "data/book_data.json"
OUTPUT_DIR = "data/book_covers"


def main():

    setup_logging("book_covers.log", use_tqdm=True)

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    with open(BOOK_DATA_JSON, "r", encoding="utf-8") as f:

        country_book_data = json.load(f)

        isbns = [
            book.get("isbn")
            for country_data in country_book_data.values()
            for book in country_data.get("books", [])
            if book.get("isbn")
        ]

        for isbn in tqdm(isbns):
            output_path = Path(OUTPUT_DIR, f"{isbn}.jpg")
            if output_path.exists():
                continue
            fetch_google_books_thumbnail(isbn, output_path)


if __name__ == "__main__":
    main()
