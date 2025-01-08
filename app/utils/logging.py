import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(log_level: str = "INFO", log_file: str = "app.log", max_file_size: int = 10_000_000, backup_count: int = 5):
    """
    Configures logging for the application.

    Args:
        log_level (str): The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file (str): Path to the log file.
        max_file_size (int): Maximum size of the log file in bytes before rotation.
        backup_count (int): Number of rotated log files to keep.
    """
    # Ensure the log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Set up the root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),  # Console logging
            RotatingFileHandler(log_file, maxBytes=max_file_size, backupCount=backup_count),  # File logging
        ],
    )

# Example usage for debugging
if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Logging setup is complete.")
    logger.debug("This is a debug message.")
    logger.error("This is an error message.")

logger = logging.getLogger(__name__)