import logging

def custom_logger(path, filename):
    logger = logging.getLogger("ManyVidsErrorCrawler")
    handler = logging.FileHandler(path + "/logs/%s.log" % filename)
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger
