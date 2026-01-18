import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tqdm import tqdm


class TqdmLoggingHandler(logging.Handler):
    """Logging handler that prints messages via tqdm.write."""

    def emit(self, record):
        try:
            msg = self.format(record)
            tqdm.write(msg)
            self.flush()
        except Exception:
            self.handleError(record)


def setup_logging(
    log_filename: str,
    log_dir: str = "logs",
    console_level: int = logging.INFO,
    file_level: int = logging.ERROR,
    max_bytes: int = 5_000_000,
    backup_count: int = 3,
    use_tqdm: bool = False,
):
    """Set up root logger with console and rotating file handlers.

    Args:
        log_filename (str): filename for log file
        log_dir (str, optional): directory for log files. Defaults to "logs".
        console_level (int, optional): minimum level for console logging. Defaults to logging.INFO.
        file_level (int, optional): minimum level for file logging. Defaults to logging.ERROR.
        max_bytes (int, optional): max size per log file before rotation. Defaults to 5_000_000.
        backup_count (int, optional): number of rotated log files to keep. Defaults to 3.
        use_tqdm (bool, optional): if True, console logs go through tqdm.write(). Defaults to False.
    """
    # Create the log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Define path to log file
    log_file = log_path / log_filename

    # Get root logger and remove existing handlers if configured
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        logger.handlers.clear()

    # --- File handler ---
    # RotatingFileHandler writes logs to a file and rotates when it reaches max_bytes
    file_handler = RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(file_handler)

    # --- Console handler ---
    # Use TqdmLoggingHandler if tqdm progress bars are enabled, otherwise normal console output
    console_handler = TqdmLoggingHandler() if use_tqdm else logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)
