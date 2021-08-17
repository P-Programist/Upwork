import os
import sqlite3
import pathlib
import datetime as dt
from loggers import custom_logger

PATH = str(pathlib.Path(__file__).parent)
LOGGER = custom_logger(PATH, "general")

##################################################
############# DATABASE CONFIGS ###################
##################################################
DB_PATH = PATH + '/results.db'
DB_TABLE_NAME = 'races'

DATABASE_PATH = pathlib.Path(DB_PATH)

CONNECTION = sqlite3.connect(DB_PATH)
CURSOR = CONNECTION.cursor()
##################################################


####################################################################################################
CSV_DATA_DIR = pathlib.Path(PATH + "/CSV")

CSV_DATA = True
if not CSV_DATA_DIR.exists() or not os.path.isdir(PATH + "/CSV"):
    CSV_DATA = False
    print('\nATTENTION: There is no "CSV" folder in %s' % PATH)
    print('IMPORTANT: Create "CSV" folder in %s\n' % PATH)


XLSX_DATA_DIR = pathlib.Path(PATH + "/XLSX")

XLSX_DATA = True
if not XLSX_DATA_DIR.exists() or not os.path.isdir(PATH + "/XLSX"):
    XLSX_DATA = False
    print('\nATTENTION: There is no "XLSX" folder in %s' % PATH)
    print('IMPORTANT: Create "XLSX" folder in %s\n' % PATH)

####################################################################################################



######################################################################
################# DATABASE CREATION FUNCTIONS ########################
######################################################################
def create(table_name):
    try:
        CURSOR.execute(CREATE_RACE_RESULT_TABLE_QUERY)
        CONNECTION.commit()
    except sqlite3.OperationalError:
        print('Table %s is already exists!' % table_name.upper())


def drop_table(table_name):
    try:
        CURSOR.execute("DROP TABLE %s;" % table_name)
        CONNECTION.commit()
    except sqlite3.OperationalError:
        print('Table %s does not exist!' % table_name.upper())
######################################################################


def check_db():
    if DATABASE_PATH.exists():
        # Uncomment the line below in case You want to recreate the Database!
        # drop_table(DB_TABLE_NAME)
        create(DB_TABLE_NAME)
        return True




CURRENT_YEAR = dt.datetime.now().year
CURRENT_MONTH = dt.datetime.now().month
CURRENT_DAY = dt.datetime.now().day

URLS = [
    'https://www.timeform.com/horse-racing/results/yesterday'
]

MONTHS = {
    1: 31, 2: 28,
    3: 31, 4: 30,
    5: 31, 6: 30,
    7: 31, 8: 31,
    9: 30, 10: 31,
    11: 30, 12: 31,
}



LAST_WEEK = dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=7)), '%-d/%-m/%y')
LAST_MONTH = dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=31)), '%-d/%-m/%y')
TODAY = dt.datetime.strftime((dt.datetime.today() - dt.timedelta(days=1)), '%-d/%-m/%y')

TIMELINES = {
    "week": LAST_WEEK,
    "month": LAST_MONTH,
    "today": TODAY
}

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
    "Betfair_SP_Order",
    "stake",
    "Won_Races",
    "Lost_Races",
    "Back_Win",
    "Lay_Win",
    "Back_ROI",
    "Lay_ROI",
    "Back_S_Rate",
    "Lay_S_Rate",
    "BackProbability",
)



CREATE_RACE_RESULT_TABLE_QUERY = '''
CREATE TABLE races(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    Betfair_SP_Order INT,
    stake INT DEFAULT 1,
    Won_Races FLOAT DEFAULT 0,
    Lost_Races FLOAT DEFAULT 0,
    Back_Win FLOAT DEFAULT 0,
    Lay_Win FLOAT DEFAULT 0,
    Back_ROI FLOAT DEFAULT 0,
    Lay_ROI FLOAT DEFAULT 0,
    Back_S_Rate FLOAT DEFAULT 0,
    Lay_S_Rate FLOAT DEFAULT 0,
    BackProbability FLOAT DEFAULT 0);'''


GENERAL_XLSX_COLUMNS = [
    "Date",
    "Time",
    "Track",
    "Distance",
    "RaceType",
    "Position",
    "HorseNumber",
    "HorseName",
    "Jokey",
    "Trainer",
    "HorseAge",
    "HorseWeight",
    "Bsp",
    "Bpsp",
    "High",
    "Low",
    "B2L",
    "L2B",
    "Runners"
]

BACK_WIN_XLSX_COLUMNS = [
    "Betfair_SP_Order",
    "Won_Races",
    "Back_Win",
    "Back_ROI",
    "Back_S_Rate",
    "BackProbability"
]


LAY_WIN_XLSX_COLUMNS = [
    "Betfair_SP_Order",
    "Lost_Races",
    "Lay_Win",
    "Lay_ROI",
    "Lay_S_Rate",
]