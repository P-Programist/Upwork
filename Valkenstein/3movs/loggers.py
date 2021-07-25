import logging
import configs


def error_logger():
    logger = logging.getLogger("3MOVS_ERRORS")
    handler = logging.FileHandler(configs.PATH + "/errors.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger


def info_logger():
    logger = logging.getLogger("3MOVS_INFO")
    handler = logging.FileHandler(configs.PATH + "/info.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger
