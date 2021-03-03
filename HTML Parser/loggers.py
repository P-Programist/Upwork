# This file is responsible for writting errors into logs directory.

import os
import logging

PATH = os.path.dirname(__file__)

if not os.path.exists(PATH + '/logs/'):
    os.makedirs(PATH + '/logs/')

logger = logging.getLogger(__name__)

file_handler = logging.FileHandler(f'{PATH}/logs/errors.log')
formater = logging.Formatter(f"%(asctime)s: %(lineno)s: %(message)s")

logger.addHandler(file_handler)
file_handler.setFormatter(formater)
logger.setLevel(logging.INFO)