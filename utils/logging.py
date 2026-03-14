"""
Logging utility for Best-Option
"""
import logging
import os
from datetime import datetime


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # File handler (optional)
        log_dir = "log"
        if os.path.exists(log_dir):
            log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger
