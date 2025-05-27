import logging
import os

def setup_logger(log_file='mdg.log'):
    """建立日誌紀錄器，輸出同時到檔案與標準輸出"""
    logger = logging.getLogger('MDGLogger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s')

    # File handler
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
