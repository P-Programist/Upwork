import logging
from static import PATH


def error_logger():
    lg = logging.Logger("ErrorLogger")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s | %(lineno)s"
    )
    handler = logging.FileHandler(PATH + "/logs/errors.log")
    handler.setFormatter(formatter)
    lg.addHandler(handler)
    lg.setLevel(logging.INFO)

    return lg
