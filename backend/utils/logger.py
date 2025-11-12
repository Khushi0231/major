
"""Logging configuration"""
import logging
from pathlib import Path

def setup_logger(name: str, log_file: str = "data/logs/dravis.log") -> logging.Logger:
    Path(log_file).parent.mkdir(exist_ok=True, parents=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
