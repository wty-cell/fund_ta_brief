import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logger(name="fund_ta_brief", log_dir="logs", max_days=30):
    os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        logger.handlers.clear()
    
    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, "run.log"),
        when="midnight",
        interval=1,
        backupCount=max_days,
        encoding="utf-8"
    )
    
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
