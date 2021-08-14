import os
import pathlib
import datetime as dt
from loggers import custom_logger

PATH = str(pathlib.Path(__file__).parent)
LOGGER = custom_logger(PATH, "general")

DB_PATH = PATH + '/results.db'
DB_TABLE_NAME = 'races'

CSV_DATA_DIR = pathlib.Path(PATH + "/csv_data")

CSV_DATA = True
if not CSV_DATA_DIR.exists() or not os.path.isdir(PATH + "/csv_data"):
    CSV_DATA = False
    print('\nATTENTION: There is no "csv_data" folder in %s' % PATH)
    print('IMPORTANT: Create "csv_data" folder in %s\n' % PATH)

CURRENT_YEAR = dt.datetime.now().year
CURRENT_MONTH = dt.datetime.now().month
CURRENT_DAY = dt.datetime.now().day

URLS = []

MONTHS = {
        1: 31, 2: 28,
        3: 31, 4: 30,
        5: 31, 6: 30,
        7: 31, 8: 31,
        9: 30, 10: 31,
        11: 30, 12: 31,
    }


for year in range(2021, CURRENT_YEAR + 1):
    MONTHS[2] = 28

    if not year % 4:
        MONTHS[2] = 29

    for month in range(1, CURRENT_MONTH + 1):
        for day in range(1, MONTHS.get(month)+1):
            date = '%d-%d-%d' % (year, month, day)
            url = 'https://www.timeform.com/horse-racing/results/%s' % date
            URLS.append(url)



HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "www.timeform.com",
    "Referer": "https://www.timeform.com/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
}

COOKIES = {
    ".AspNet.ApplicationCookie": "exJxWpZ8rvlbYojns4ouY07QGYymdVLAu_pFewAzh6pCADLfU30o6dxhMlyLTt2Dz5BGn4QXE6N1DdaQkOLSg8R7rd1tfXG6Of_FF80T5fSzbrMRItTv_-Dt2kDxvlKAvebYAANUHaT4MosWjsItN_uxiV1z43p2wGKn-Y-9JbYkXieyrQDNiL9WwxNkiIFOfhfTbY7xO4sOaWt7QBvzGBDaYpnce-E3AS5nQ9xG7zxYm7CBoEtesa87EAKPvNmDXDXAmocYuTyOCaJtVoeqQB3930_nA_t4w1mcQRhH1cc8ouNPQ9lPAGjznP1XrLfJX_b6s2OETAR7mNAC-Pq1HxT-1Vxgh19j9_znpHU5umLsyp8g6vjtaYzDppdXVM_iNuaFbLc1qY7FTmVi-Jy60IF9Fg391x09sDVIz1clGUfG8cqCOJ9vMch0vtG5jpanJiMKEtjhH3VAlr4Ee9O33IWpFzU",
    "ARRAffinity": "58959f315ae110c77c27b360c2c2aa988f5fa92288eacf5bf282dfe6e588a5e9",
    "ASLBSA": "edcea0edb343caeb5bfe6063a9f48f61d10f5975a23a4551d1daca85b2743553,0a72ced5e226f97f71fc726331f5674e8dceb21b0942efe4be7e6e60c5e28d96,81e077dbeef5ae66eaa683afd6e2628be800f2f043cad6bc40f125266ddce13d",
    "ASLBSACORS": "edcea0edb343caeb5bfe6063a9f48f61d10f5975a23a4551d1daca85b2743553,0a72ced5e226f97f71fc726331f5674e8dceb21b0942efe4be7e6e60c5e28d96,81e077dbeef5ae66eaa683afd6e2628be800f2f043cad6bc40f125266ddce13d",
    "ASP.NET_SessionId": "2elcxmku1w0fcs4ggufkyf0j",
    "TF-CookiePrivacyPolicy": "Allow",
    "TF-UpgradePopUp": "Seen",
    "TFM": "DeviceId=d77e652f-373d-4954-8d00-60d197b329bf",
}


DB_COLUMS = (
    "date",
    "time",
    "track",
    "distance",
    "race_type",
    "position",
    "horse_number",
    "horse_name",
    "jokey",
    "trainer",
    "horse_age",
    "horse_weight",
    "bsp",
    "bpsp",
    "high",
    "low",
    "B2L",
    "L2B",
    "runners",
    "trap",
    "stake",
    "back_winners",
    "lay_winners",
    "back_win",
    "lay_win",
    "back_roi",
    "lay_roi",
    "back_s_rate",
    "lay_s_rate",
    "back_probability",
)



CREATE_RACE_RESULT_TABLE_QUERY = '''
CREATE TABLE races(
    date VARCHAR(20),
    time VARCHAR(10),
    track VARCHAR(30),
    distance VARCHAR(15),
    race_type VARCHAR(20),
    position INT,
    horse_number INT,
    horse_name VARCHAR(50),
    jokey VARCHAR(30),
    trainer VARCHAR(30),
    horse_age FLOAT,
    horse_weight VARCHAR(10),
    bsp FLOAT,
    bpsp FLOAT,
    high FLOAT,
    low FLOAT,
    B2L FLOAT,
    L2B FLOAT,
    runners INT,
    trap INT,
    stake INT DEFAULT 1,
    back_winners FLOAT DEFAULT 0,
    lay_winners FLOAT DEFAULT 0,
    back_win FLOAT DEFAULT 0,
    lay_win FLOAT DEFAULT 0,
    back_roi FLOAT DEFAULT 0,
    lay_roi FLOAT DEFAULT 0,
    back_s_rate FLOAT DEFAULT 0,
    lay_s_rate FLOAT DEFAULT 0,
    back_probability FLOAT DEFAULT 0);'''

