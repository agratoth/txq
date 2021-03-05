import logging

LOGGER_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def get_file_handler():
    LOG_PATH = './base.log'

    file_handler = logging.FileHandler(LOG_PATH)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(LOGGER_FORMAT))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger