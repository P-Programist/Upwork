import csv
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

if not CSV_DATA_DIR.exists() or not os.path.isdir(PATH + "/CSV"):
    print('\nATTENTION: There is no "CSV" folder in %s' % PATH)
    os.mkdir(PATH + '/CSV')
    print('IMPORTANT: The "CSV" folder has been created successfully in "%s"\n' % PATH)


XLSX_DATA_DIR = pathlib.Path(PATH + "/XLSX")

if not XLSX_DATA_DIR.exists() or not os.path.isdir(PATH + "/XLSX"):
    print('\nATTENTION: There is no "XLSX" folder in %s' % PATH)
    os.mkdir(PATH + '/XLSX')
    print('IMPORTANT: The "XLSX" folder has been created successfully in "%s"\n' % PATH)
####################################################################################################



######################################################################
################# DATABASE CREATION FUNCTIONS ########################
######################################################################
def create_table(table_name):
    try:
        CURSOR.execute(CREATE_RACE_RESULT_TABLE_QUERY)
        CONNECTION.commit()
    except sqlite3.OperationalError:
        print('Table %s is already exists!' % table_name.upper())


def check_db():
    if DATABASE_PATH.exists():
        table_exists_sql = "SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';"
        query = CURSOR.execute(table_exists_sql)
        if not query.fetchall():
            create_table(DB_TABLE_NAME)
            return 2
        return 1
    return 0
######################################################################


def get_race_type_name(header):
    if 'HURDLE' in header:
        race_type_name = 'OTHER HURDLE'
        if 'HANDICAP' in header:
            race_type_name = 'HANDICAP HURDLE'
        elif 'MAIDEN' in header:
            race_type_name = 'MAIDEN HURDLE'
        elif 'JUVENILE' in header:
            race_type_name = 'JUVENILE HURDLE'
        elif 'NOVICES' in header:
            race_type_name = 'NOVICES HURDLE'

    elif 'STAKES' in header:
        race_type_name = 'OTHER FLAT'
        if 'MAIDEN' in header:
            race_type_name = 'MAIDEN STAKES'
        elif 'NOVICE' in header:
            race_type_name = 'NOVICE STAKES'
        elif 'SELLING' in header:
            race_type_name = 'SELLING STAKES'

    elif 'HANDICAP' in header:
        race_type_name = 'HANDICAP'
        if 'CHASE' in header:
            race_type_name = 'CHASE HANDICAP'
        elif 'SELLING' in header:
            race_type_name = 'SELLING HANDICAP'
    else:
        race_type_name = ' '.join(header[-3:-1])
    
    return race_type_name



URL = 'https://www.timeform.com/horse-racing/results/yesterday'


CURRENT_YEAR = dt.datetime.now().year
CURRENT_MONTH = dt.datetime.now().month
CURRENT_DAY = dt.datetime.now().day



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
    ".AspNet.ApplicationCookie": "Zd-6Jjrh1XedYEINXxh9QmVzOiAEFvolcX6VCVX7BBesErbnieAZt25Girq_E3sraX8HLk8K4voE-7QBYtdjvtLZsbDTumDVdHB2sJlcb4L1dMypXAgaBa0JHYONK48kzyFK_yWe-VqppmlVSzEGR1jWzWGS_SnY8PZqnOQnv4D9nNf1S71lSFTqRPmQnxYyJiWoJdYrSB5c0tANrtVfkrb6BBexwPuXn9BbZ96eh2Stq-wjgaNVo_NLAllxoe5s38APATB1ojC4Q-VrhQa35zIhmEtXLARPfyZ7_C1hw2mrN2nzHePLAEHSbMIgLG9nCD2FDwFpHHmL-xxOUKpbTkAYj5Sww6O_wCLyW0DfqzH-6RcFveR2oVUMLHPZzL_oxRKWFgZ6sQ-DWaWQtZT26eh2AxO200pAJcG8uwaURZVQ_6R0k87cjij0AQUHGntrOV6-P4Fw1HT82UnNz4cOKbFOFsM",
    "ARRAffinity": "c6f29867043fc4d89919a10a8b4f179c6019ba9f45ee19561219d7cdc0fa20ba",
    "ASLBSA": "6227e485cfa5652212f4a30249a2ee8316d9030eef4fd24ab7d24dacfa9a1804,b51843e69dd1f73dfa83a72a15c2303b80a8ef35bce36ade013e0f1356891fcb,a4b51a5fbeb74b972c1a2a7a81843751791fa7ed7d63fca6012d495823104469",
    "ASLBSACORS": "6227e485cfa5652212f4a30249a2ee8316d9030eef4fd24ab7d24dacfa9a1804,b51843e69dd1f73dfa83a72a15c2303b80a8ef35bce36ade013e0f1356891fcb,a4b51a5fbeb74b972c1a2a7a81843751791fa7ed7d63fca6012d495823104469",
    "ASP.NET_SessionId": "55ize12xvdjqs0fmaebfmuis",
    "TF-CookiePrivacyPolicy": "Allow",
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
    runners INT);'''


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

BACK_LAY_XLSX_COLUMNS = [
    'Betfair_SP_Order',
    'Back_Win',
    'Winners',
    'Back_ROI',
    'Back_S_Rate',
    'BackProbability',
    '',
    'Betfair_SP_Order',
    "Lost_Races",
    "Lay_Win",
    "Lay_ROI",
    "Lay_S_Rate",
]