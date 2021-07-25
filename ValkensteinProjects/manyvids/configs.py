import logging
from pathlib import Path

PROXY = (
    "http://64.17.30.238:63141",
    "http://46.223.255.8:8080",
    "http://37.49.127.234:3128",
    "http://144.76.42.215:8118",
    "http://157.230.103.189:36366",
    "http://46.223.255.13:3128",
    "http://195.201.34.206:80",
    "http://192.109.165.57:80",
    "http://46.5.252.50:3128",
    "http://85.216.127.188:3128",
    "http://46.237.255.4:8080",
    "http://192.109.165.72:80",
    "http://192.109.165.193:80",
    "http://192.109.165.54:80",
    "http://192.109.165.195:80",
    "http://167.172.171.151:37386",
    "http://136.243.211.104:80",
    "http://134.122.93.93:8080",
    "http://46.5.252.55:8080",
    "http://37.49.127.227:8080",
    "http://46.237.255.13:3128",
    "http://91.89.89.7:3128",
    "http://109.193.195.7:8080",
    "http://82.212.62.29:8080",
    "http://46.5.252.52:8080",
    "http://95.208.208.227:3128",
    "http://134.3.255.7:8080",
    "http://134.3.255.5:8080",
    "http://46.237.255.11:8080",
    "http://149.172.255.14:8080",
    "http://109.193.195.6:3128",
    "http://109.193.195.10:8080",
    "http://217.8.51.206:8080",
    "http://91.89.89.2:8080",
    "http://192.109.165.225:80",
    "http://192.109.165.135:80",
    "http://178.128.143.54:8080",
    "http://185.204.187.61:5085",
    "http://37.120.192.154:8080",
    "http://167.71.5.83:8080",
    "http://212.32.242.111:3128",
    "http://165.22.81.30:44608",
    "http://203.33.113.177:80",
    "http://82.64.183.22:8080",
    "http://154.16.63.16:3128",
    "http://23.251.138.105:8080",
    "http://3.213.139.74:8888",
    "http://132.226.25.214:3128",
    "http://65.160.224.144:80",
    "http://176.9.75.42:8080",
    "http://3.136.37.78:80",
    "http://205.185.118.53:80",
    "http://77.247.126.158:44355",
    "http://128.199.214.87:3128",
    "http://198.50.163.192:3129",
    "http://88.198.50.103:8080",
    "http://13.229.90.80:3128",
    "http://172.104.43.191:82",
    "http://138.68.60.8:8080",
    "http://209.97.150.167:8080",
    "http://161.35.70.249:3128",
    "http://191.96.42.80:8080",
    "http://128.199.202.122:3128",
    "http://167.71.5.83:8080",
    "http://132.226.24.246:3128",
    "http://206.161.234.197:80",
    "http://208.80.28.208:8080",
)


PATH = str(Path(__file__).parent)
URLS = [
    "https://www.manyvids.com/MVGirls/",
    "https://www.manyvids.com/MVTrans/",
    "https://www.manyvids.com/MVBoys/",
]

COOKIES = {
    "ageCheckDisclaimer": "1",
    "AWSALB": "/R60UVphP2j97IDgn4gXkKA91b/b/b5s7rmMrYKxzqckxY2ezOQuIT7w0yBikd48+oHcVyxQ/wiA+Yj+55Smt3vlPtPtCjPuOOzJDFwyg51yQhpcsn92sKMkrDF9COPOxzHfHqjcahNw79V9o0D06x9EAodi+eNYECM+WUV1IbVDwNCRAoKsP9KkfcNvFw==",
    "AWSALBCORS": "/R60UVphP2j97IDgn4gXkKA91b/b/b5s7rmMrYKxzqckxY2ezOQuIT7w0yBikd48+oHcVyxQ/wiA+Yj+55Smt3vlPtPtCjPuOOzJDFwyg51yQhpcsn92sKMkrDF9COPOxzHfHqjcahNw79V9o0D06x9EAodi+eNYECM+WUV1IbVDwNCRAoKsP9KkfcNvFw==",
    "contentPopup": "false",
    "dataSectionTemp": "0",
    "PHPSESSID": "XBedjQLSKCwzhnR22H1h0Rad09rCniRNeAR4wGyH",
    "privacyPolicyRead": "1",
    "timezone": "Asia/Colombo",
    "XSRF-TOKEN": "eyJpdiI6ImtQVTdmbHBaSnk3dFI0SXRQUEh1bEE9PSIsInZhbHVlIjoiWUprVXlCcG42K29YWjVCVmJVR3c4aCtLMWhwcSt2ZkZ1MVhBeXNTc0tWVFwvelFFdXg0TDFUdnRMQWdXdXNrOFkiLCJtYWMiOiJjMTc1NzcwNjc4MWFhMmI3NmRkZGRlMDc1Y2ZjZGVkZWQ5YmMyYzgwNWEyZDQzY2Y5MjMxODkzMTg2NmNmNDkzIn0=",
}


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Cookie": "AWSALB=/R60UVphP2j97IDgn4gXkKA91b/b/b5s7rmMrYKxzqckxY2ezOQuIT7w0yBikd48+oHcVyxQ/wiA+Yj+55Smt3vlPtPtCjPuOOzJDFwyg51yQhpcsn92sKMkrDF9COPOxzHfHqjcahNw79V9o0D06x9EAodi+eNYECM+WUV1IbVDwNCRAoKsP9KkfcNvFw==; AWSALBCORS=/R60UVphP2j97IDgn4gXkKA91b/b/b5s7rmMrYKxzqckxY2ezOQuIT7w0yBikd48+oHcVyxQ/wiA+Yj+55Smt3vlPtPtCjPuOOzJDFwyg51yQhpcsn92sKMkrDF9COPOxzHfHqjcahNw79V9o0D06x9EAodi+eNYECM+WUV1IbVDwNCRAoKsP9KkfcNvFw==; XSRF-TOKEN=eyJpdiI6ImtQVTdmbHBaSnk3dFI0SXRQUEh1bEE9PSIsInZhbHVlIjoiWUprVXlCcG42K29YWjVCVmJVR3c4aCtLMWhwcSt2ZkZ1MVhBeXNTc0tWVFwvelFFdXg0TDFUdnRMQWdXdXNrOFkiLCJtYWMiOiJjMTc1NzcwNjc4MWFhMmI3NmRkZGRlMDc1Y2ZjZGVkZWQ5YmMyYzgwNWEyZDQzY2Y5MjMxODkzMTg2NmNmNDkzIn0%3D; PHPSESSID=XBedjQLSKCwzhnR22H1h0Rad09rCniRNeAR4wGyH; dataSectionTemp=0; privacyPolicyRead=1; ageCheckDisclaimer=1; timezone=Asia%2FColombo; contentPopup=false",
    "Host": "www.manyvids.com",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
}


def main_logger():
    logger = logging.getLogger("ManyVidsErrorCrawler")
    handler = logging.FileHandler(PATH + "/logs/errors.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger


def info_logger():
    logger = logging.getLogger("ManyVidsInfoCrawler")
    handler = logging.FileHandler(PATH + "/logs/info.log")
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger
