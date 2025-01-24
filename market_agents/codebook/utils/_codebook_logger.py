import logging
from pathlib import Path

# Create a log directory if it doesn't exist
log_dir = Path(__file__).parent / 'codebook_logs'
log_dir.mkdir(exist_ok=True)

# Configure logging
def _codebook_logger(filename: str):
    """
    Create and configure a logger for the given filename.

    This function sets up a logger with a file handler that writes log messages
    to a file in the 'codebook_logs' directory. The log file is named after the
    provided filename with a '.log' extension.

    Args:
        filename (str): The name to be used for the logger and the log file.

    Returns:
        logging.Logger: A configured logger object.

    The logger is configured with the following settings:
    - Log level: DEBUG
    - Log format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    - Log file location: 'codebook_logs/{filename}.log'
    """
    logger = logging.getLogger(filename)
    log_file = log_dir / f'{filename}.log'
    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger