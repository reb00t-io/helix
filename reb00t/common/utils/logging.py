import logging
import os

logger = None

def init_logging(log_file='.log/coda.log', log_level=logging.INFO):
    global logger
    if logger is not None:
        return logger

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a logger
    logger = logging.getLogger('coda')
    logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create file handler and set level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.propagate = False

    return logger

# Usage in other files
# from your_logging_module import init_logging

# logger = init_logging()
# logger.info("This is an info message")
