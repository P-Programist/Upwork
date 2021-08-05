import pathlib

PATH = str(pathlib.Path(__file__).parent)

URLS = (
    'https://www.timeform.com/horse-racing/results/2021-07-19',
    'https://www.timeform.com/horse-racing/results/2021-07-18',
    'https://www.timeform.com/horse-racing/results/2021-07-19',
    'https://www.timeform.com/horse-racing/results/2021-07-20',
    'https://www.timeform.com/horse-racing/results/2021-07-21',
    'https://www.timeform.com/horse-racing/results/2021-07-22',

    'https://www.timeform.com/horse-racing/results/2021-07-23',
    'https://www.timeform.com/horse-racing/results/2021-07-24',
    'https://www.timeform.com/horse-racing/results/2021-07-25',
    'https://www.timeform.com/horse-racing/results/2021-07-26',
    'https://www.timeform.com/horse-racing/results/2021-07-27',
    'https://www.timeform.com/horse-racing/results/2021-07-28',

    'https://www.timeform.com/horse-racing/results/2021-07-29',
    'https://www.timeform.com/horse-racing/results/2021-07-30',
    'https://www.timeform.com/horse-racing/results/2021-07-31',
    'https://www.timeform.com/horse-racing/results/2021-08-01',
    'https://www.timeform.com/horse-racing/results/2021-08-02',
    'https://www.timeform.com/horse-racing/results/2021-08-03',
    'https://www.timeform.com/horse-racing/results/2021-08-04',
    )

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

    "back_win",
    "lay_win",
    "back_roi",
    "back_s_rate",
    "back_probability",

    "lay_roi",
    "lay_s_rate",
    "number_of_races"
)


CSV_COLUMNS = (
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

STAKE = 1