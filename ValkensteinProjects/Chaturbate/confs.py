import logging

proxies = (
    {"http": "64.17.30.238:63141"},
    {"http": "46.223.255.8:8080"},
    {"http": "37.49.127.234:3128"},
    {"http": "144.76.42.215:8118"},
    {"http": "157.230.103.189:36366"},
    {"http": "46.223.255.13:3128"},
    {"http": "195.201.34.206:80"},
    {"http": "192.109.165.57:80"},
    {"http": "46.5.252.50:3128"},
    {"http": "85.216.127.188:3128"},
    {"http": "46.237.255.4:8080"},
    {"http": "192.109.165.72:80"},
    {"http": "192.109.165.193:80"},
    {"http": "192.109.165.54:80"},
    {"http": "192.109.165.195:80"},
    {"http": "167.172.171.151:37386"},
    {"http": "136.243.211.104:80"},
    {"http": "134.122.93.93:8080"},
    {"http": "46.5.252.55:8080"},
    {"http": "37.49.127.227:8080"},
    {"http": "46.237.255.13:3128"},
    {"http": "91.89.89.7:3128"},
    {"http": "109.193.195.7:8080"},
    {"http": "82.212.62.29:8080"},
    {"http": "46.5.252.52:8080"},
    {"http": "95.208.208.227:3128"},
    {"http": "134.3.255.7:8080"},
    {"http": "134.3.255.5:8080"},
    {"http": "46.237.255.11:8080"},
    {"http": "149.172.255.14:8080"},
    {"http": "109.193.195.6:3128"},
    {"http": "109.193.195.10:8080"},
    {"http": "217.8.51.206:8080"},
    {"http": "91.89.89.2:8080"},
    {"http": "192.109.165.225:80"},
    {"http": "192.109.165.135:80"},
    ### Niderlands ###
    {"http": "178.128.143.54:8080"},
    {"http": "185.204.187.61:5085"},
    {"http": "37.120.192.154:8080"},
    {"http": "167.71.5.83:8080"},
    {"http": "212.32.242.111:3128"},
)

cookies = {
    "__cf_bm": "363feb4c31a5cc0c6fcb31e28e7718f3bce03c2a-1625674107-1800-AaNL+T7cbKcwiRDgr3EoDnZd0gy/WO3/0mJdy0kkQ+mqBfeRwVXy1zmsGyG3fwfn/fhohwpG2AUHQmTM5OO1n/g=",
    "__utfpp": "f:trnx1f11ddc0b432ae1e51fa213680848fa6:1m1AD6:1fd5mVVSMxO_p8PnucRxF1QYbn4",
    "affkey": "eJyrVipSslJQUqoFAAwfAk0=",
    "ag": '{"20to30-cams":24}',
    "agreeterms": "1",
    "csrftoken": "xjirH6m6lQJgma7q999XTyGvxtmWTzYqUKRsF62KvnvFvtDIf8DZwyru6WDNYhjw",
    "dwf_s_a": "True",
    "sbr": "sec:sbr4278e21b-9e06-4484-954a-36bf4f71aa49:1m19rL:LaEeLws-AFy-1XJ6LRin4lMGtlY",
    "sessionid": "0lqbmt72uslaul6s0e1cd1q4t1rk9uku",
    "stcki": "ofndNK=0\\054PRh_pw=1",
}


def main_logger():
    logger = logging.getLogger("ChaturbateErrorCrawler")
    handler = logging.FileHandler("/www/var/python/chaturbate/errors.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger


def info_logger():
    logger = logging.getLogger("ChaturbateInfoCrawler")
    handler = logging.FileHandler("/www/var/python/chaturbate/info.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger
