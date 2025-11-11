import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = "/app/logs"
LOG_FILE = os.path.join(LOG_DIR, "mosquitto.log")

def setup_logger(logger_name="webhook_logger"):
    """
    Sets up a timed rotating file logger that writes to a single file.
    """
    # Create log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Create the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if this is called multiple times
    if logger.hasHandlers():
        return logger

    # Set up a handler
    # This will rotate the log file every day (when="midnight")
    # and keep 7 days of backups (backupCount=7)
    handler = TimedRotatingFileHandler(
        LOG_FILE,
        when="midnight",
        interval=1,
        backupCount=7
    )

    # Define the log format
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Prevent logs from bubbling up to the root logger
    logger.propagate = False

    print(f"✅ Logging all webhook events to {LOG_FILE}")

    return logger

# Create a single logger instance to be imported by other files
logger = setup_logger()
