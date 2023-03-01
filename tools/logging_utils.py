import sys
import logging
from logging.handlers import TimedRotatingFileHandler
FORMATTER = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

def get_console_handler(level=logging.INFO):
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    console_handler.setLevel = level
    return console_handler

def get_file_handler(log_file='logfile.log', level=logging.INFO):
    file_handler = TimedRotatingFileHandler(log_file, when='midnight')
    file_handler.setFormatter(FORMATTER)
    file_handler.setLevel=level
    return file_handler

def get_logger(logger_name, log_folder='/var/log/automation', log_file = None, level=logging.INFO):
    if not log_file: 
        log_file = f'{log_folder}{logger_name}.log'
    logger = logging.getLogger(logger_name)
    logger.setLevel(level=level)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file=log_file, level=level))
    logger.propagate = False
    return logger
