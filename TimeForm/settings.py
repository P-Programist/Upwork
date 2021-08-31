import os
import logging
import sqlite3
import pathlib


PATH = str(pathlib.Path(__file__).parent)

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
        elif 'CHAMPION' in header:
            race_type_name = 'CHAMPION HURDLE'

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

    elif 'RELKEEL' in header:
        race_type_name = 'RELKEEL'
        if 'HURDLE' in header:
            race_type_name = 'RELKEEL HURDLE'

    elif 'CHASE' in header:
        race_type_name = 'CHASE'
        if 'HOUSE' in header:
            race_type_name = 'HOUSE CHASE'
        elif 'NOVICES' in header:
            race_type_name = 'NOVICES CHASE'

    else:
        race_type_name = ' '.join(header[-3:-1])

    return race_type_name.replace('(', '').replace(')', '')


######################################################################
####################### LOGGING CONFIGURATIONS #######################
######################################################################
def custom_logger(path, filename):
    logger = logging.getLogger("Timeform")
    handler = logging.FileHandler(path + "/%s.log" % filename)
    formater = logging.Formatter(
        "%(asctime)s| %(message)s ---> %(lineno)s", "%Y-%m-%d %H:%m"
    )
    handler.setFormatter(formater)
    logger.addHandler(handler)
    level = logging.INFO
    logger.setLevel(level)

    return logger


LOGGER = custom_logger(PATH, "events")
######################################################################

URL = 'https://www.timeform.com/horse-racing/results/yesterday'
HOME_URL = 'https://www.timeform.com/horse-racing'
LOGIN_URL = 'https://www.timeform.com/horse-racing/account/sign-in?returnUrl=%2Fhorse-racing%2F'


FILTER_RACE = input(
    '\nFilter by Race Type(press Enter if there is no filters): ').upper()
FILTER_DISTANCE = input(
    '\nFilter by Distance(press Enter if there is no filters): ').lower()


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
    "__qca": "P0-1958240426-1629673197218",
    "__RequestVerificationToken_L2hvcnNlLXJhY2luZw2": "umrvl-XkEhCb-EH2_mq2UvsaOB1tyZhRPG2ZYETvUxinwzqdyao_DIOVgyZNp6ux2vgMNNO73HaYDkkUQUl9jo10Yjg1",
    "_fbp": "fb.1.1629673197077.388472838",
    "_ga": "GA1.2.177661324.1629673196",
    "_ga_76L4M34CLJ": "GS1.1.1629675314.2.1.1629675342.0",
    "_privy_BC6B11B656215F90B8373EC5": "{\"uuid\":\"27835cd4-1cc4-45c4-9285-8cafa5dca4f0\"}",
    "_vis_opt_s": "1|",
    "_vwo_uuid_v2": "DB8BF75C27191CC908E25E599F7A99169|4af3475c1829209f92ec1d669ec64913",
    ".AspNet.ApplicationCookie": "iJYFeoGrKzUwWo31jNaUOppDc7VsyQTGHsEogQnSTkHtUCCkQ3klwgMhhae5Yd4ifzfPbmvtakHm77yGiefxg4pwn3yGOrLUGFv_fzfTIhm6VtURr8K_i15r1pm2EBTV62wz7Ae__xwKo4kGMRf0jyQXW6uw1pnx2nNbSH6OjgmUQ2V4vNbgyNsn1j-k_zD7F63ObPt8yUw-v2EhS1f0aevab9lNyIw4JPZVCSn3L3IJcKGL5f84qQOMKLKD0qureb1Xsq-mkEC1zunpsm8SOplViOgrUj3kOAqqFIyIEaoicCa5y3cv6NTENrL71Ri5HSglQ-FBJfrkn5ECmVB7LRxnNjqGrq34eYzPOHufa5a1dmJ-rIGr39PnGk3k05VaOk_pWIZHaFq_YvpMqzqtdKiPrbq2hQmps-1A2Jj8-NrvROq0LQDE3URXTmF6JVJSVhCyewaY78INuHdL4olc74X6H7k",
    "ai_user": "wOUvR|2021-08-22T23:00:34.604Z",
    "ARRAffinity": "c6f29867043fc4d89919a10a8b4f179c6019ba9f45ee19561219d7cdc0fa20ba",
    "ASLBSA": "6227e485cfa5652212f4a30249a2ee8316d9030eef4fd24ab7d24dacfa9a1804,b51843e69dd1f73dfa83a72a15c2303b80a8ef35bce36ade013e0f1356891fcb,a4b51a5fbeb74b972c1a2a7a81843751791fa7ed7d63fca6012d495823104469",
    "ASLBSACORS": "6227e485cfa5652212f4a30249a2ee8316d9030eef4fd24ab7d24dacfa9a1804,b51843e69dd1f73dfa83a72a15c2303b80a8ef35bce36ade013e0f1356891fcb,a4b51a5fbeb74b972c1a2a7a81843751791fa7ed7d63fca6012d495823104469",
    "ASP.NET_SessionId": "xw5ripz3qvkhx0fojwo2zirc",
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
    "Runners"
]

BACK_LAY_XLSX_COLUMNS = [
    'Betfair_SP_Order',
    'TotalRaces',
    'Winners',
    'Back_Win',
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
