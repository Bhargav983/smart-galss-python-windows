import logging
import os
import sys

def setup_logger():
    """
    Sets up the application logger to both console and file.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "app.log")
    
    # Create logger
    logger = logging.getLogger("HeyCyanMVP")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger

# Singleton instance
logger = setup_logger()
