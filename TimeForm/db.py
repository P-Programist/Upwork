import csv
import sqlite3

import openpyxl

from settings import (
    PATH, 
    DB_COLUMS, 
    CREATE_RACE_RESULT_TABLE_QUERY, 
    DB_PATH, CSV_DATA,
    DB_TABLE_NAME,
    TIMELINES,
    GENERAL_XLSX_COLUMNS,
    BACK_WIN_XLSX_COLUMNS,
    LAY_WIN_XLSX_COLUMNS
)


CONNECTION = sqlite3.connect(DB_PATH)
CURSOR = CONNECTION.cursor()

INSERT_COLUMNS_ROW = ', '.join(DB_COLUMS)


def upload_csv(csv_file):
    reader = csv.reader(csv_file)
    try:
        next(reader)
        return reader
    except StopIteration:
        return []


def create(table_name):
    try:
        CURSOR.execute(CREATE_RACE_RESULT_TABLE_QUERY)
    except sqlite3.OperationalError:
        print('Table %s is already exists!' % table_name.upper())


def drop_table(table_name):
    try:
        CURSOR.execute("DROP TABLE %s;" % table_name)
        CONNECTION.commit()
    except sqlite3.OperationalError:
        print('Table %s does not exist!' % table_name.upper())


def insert(table_name, columns, race_types, reader):
    current_date = None

    for row in reader:
        race_date = row[0]
        race_time = row[1]
        race_type = row[4]
        position = row[5]

        if race_types and current_date == race_date:
            if race_type in race_types:
                if position == '1':
                    CURSOR.execute(
                        'UPDATE %s \
                            SET \
                                back_winners = back_winners + 1, \
                                back_win = (bsp-1) * stake, \
                                lay_win = -(bsp-1) * stake \
                            WHERE race_type = \'%s\' AND date = \'%s\' AND time = \'%s\';' % (table_name, race_type.replace('\'',''), race_date, race_time))

                    CONNECTION.commit()

                    CURSOR.execute(
                        'UPDATE %s \
                            SET \
                                back_roi = back_win / back_winners, \
                                lay_roi = lay_win / lay_winners, \
                                back_s_rate = (back_winners / (back_winners + lay_winners)) * 100, \
                                lay_s_rate = (lay_winners / (back_winners + lay_winners)) * 100, \
                                back_probability = (back_winners / (back_winners + lay_winners)) * 100 \
                            WHERE race_type = \'%s\' AND date = \'%s\' AND time = \'%s\';' % (table_name, race_type.replace('\'',''), race_date, race_time))

                    CONNECTION.commit()
                else:
                    CURSOR.execute(
                        'UPDATE %s \
                            SET \
                                lay_winners = lay_winners + 1, \
                                back_win = back_win - stake, \
                                lay_win = lay_win + stake \
                            WHERE race_type = \'%s\' AND time = \'%s\' AND time = \'%s\';' % (table_name, race_type.replace('\'',''), race_date, race_time))

                    CONNECTION.commit()
                    
                    CURSOR.execute(
                        'UPDATE %s \
                            SET \
                                back_roi = back_win / back_winners, \
                                lay_roi = lay_win / lay_winners, \
                                back_s_rate = (back_winners / (back_winners + lay_winners)) * 100, \
                                lay_s_rate = (lay_winners / (back_winners + lay_winners)) * 100, \
                                back_probability = (back_winners / (back_winners + lay_winners)) * 100 \
                            WHERE race_type = \'%s\' AND time = \'%s\' AND time = \'%s\';' % (table_name, race_type.replace('\'',''), race_date, race_time))
                    CONNECTION.commit()
            else:
                CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
                    table_name, columns), row)

                CONNECTION.commit()
    
        else:
            if position == '1':
                back_win_formula = (float(row[12]) - 1) * 1
                lay_win_formula = -(float(row[12]) - 1) * 1
                back_roi = back_win_formula
                lay_roi = lay_win_formula
                back_s_rate = 100
                lay_s_rate = 0
                back_probability = back_s_rate

                row.extend([1, 1, 0, back_win_formula, lay_win_formula, back_roi, lay_roi, back_s_rate, lay_s_rate, back_probability])
            else:
                back_win_formula = -1
                lay_win_formula = 1
                back_roi = back_win_formula
                lay_roi = lay_win_formula
                back_s_rate = 0
                lay_s_rate = 100
                back_probability = back_s_rate

                row.extend([1, 0, 1, back_win_formula, lay_win_formula, back_roi, lay_roi, back_s_rate, lay_s_rate, back_probability])

            CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
                    table_name, columns), row)

            CONNECTION.commit()
        current_date = race_date

        


def select(column_name: str, table_name: str, conditions: str=None):
    if conditions:
        sql = "SELECT %s FROM %s %s;" % (column_name, table_name, conditions)
    else:
        sql = "SELECT %s FROM %s;" % (column_name, table_name)

    result = CURSOR.execute(sql)
    
    for res in result.fetchall():
        yield res


def data_uploader():
    drop_table(DB_TABLE_NAME)
    create(DB_TABLE_NAME)

    if CSV_DATA:
        csv_file = open(PATH + '/CSV/data.csv', 'r')
        csv_reader = upload_csv(csv_file)
        csv_reader_copy = tuple(csv_reader)

        race_types = tuple({line[4] for line in csv_reader})
        insert(DB_TABLE_NAME, INSERT_COLUMNS_ROW, race_types, csv_reader_copy)

        csv_file.close()



def db_to_xslx_today():
    ####################################################################################################
    ################################## TODAY RACES GENERAL INFORMATION #################################
    ####################################################################################################

    today_workbook_general = openpyxl.Workbook()
    today_worksheet_general = today_workbook_general.active
    today_race_general = select(','.join(DB_COLUMS[:19]), DB_TABLE_NAME, 'WHERE date = \'%s\'' % TIMELINES.get('today'))

    today_worksheet_general.append(GENERAL_XLSX_COLUMNS)

    for row in today_race_general:
        today_worksheet_general.append(row)
    today_workbook_general.save(PATH + '/XLSX/TODAY/todayRacesGeneral.xlsx')


    ####################################################################################################
    ################################# TODAY RACES BACK WIN INFORMATION #################################
    ####################################################################################################

    today_workbook_back_win = openpyxl.Workbook()
    today_worksheet_back_win = today_workbook_back_win.active
    today_race_details = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[21::2])), DB_TABLE_NAME, 'WHERE date = \'%s\'' % TIMELINES.get('today'))

    today_worksheet_back_win.append(BACK_WIN_XLSX_COLUMNS)

    for row in today_race_details:
        today_worksheet_back_win.append(row)
    today_workbook_back_win.save(PATH + '/XLSX/TODAY/todayRacesBackWin.xlsx')


    ####################################################################################################
    ################################## TODAY RACES LAY WIN INFORMATION #################################
    ####################################################################################################

    today_workbook_lay_win = openpyxl.Workbook()
    today_worksheet_lay_win = today_workbook_lay_win.active
    today_race_details = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[22::2])), DB_TABLE_NAME, 'WHERE date = \'%s\'' % TIMELINES.get('today'))

    today_worksheet_lay_win.append(LAY_WIN_XLSX_COLUMNS)

    for row in today_race_details:
        today_worksheet_lay_win.append(row)
    today_workbook_lay_win.save(PATH + '/XLSX/TODAY/todayRacesLayWin.xlsx')
    

def db_to_xslx_last_month():
    ####################################################################################################
    ################################ LAST MONTH RACES GENERAL INFORMATION ##############################
    ####################################################################################################

    lastMonth_workbook_general = openpyxl.Workbook()
    lastMonth_worksheet_general = lastMonth_workbook_general.active
    month_id = next(select('id', DB_TABLE_NAME, 'WHERE date = \'%s\' LIMIT 1' % TIMELINES.get('month')))
    month_race = select(','.join(DB_COLUMS[:19]), DB_TABLE_NAME, 'WHERE id >= %s' % month_id)

    lastMonth_worksheet_general.append(GENERAL_XLSX_COLUMNS)

    for row in month_race:
        lastMonth_worksheet_general.append(row)
    lastMonth_workbook_general.save(PATH + '/XLSX/LAST_MONTH/lastMonthRacesGeneral.xlsx')


    ####################################################################################################
    ############################### LAST MONTH RACES BACK WIN INFORMATION ##############################
    ####################################################################################################

    lastMonth_workbook_back_win = openpyxl.Workbook()
    lastMonth_worksheet_back_win = lastMonth_workbook_back_win.active
    month_id = next(select('id', DB_TABLE_NAME, 'WHERE date = \'%s\' LIMIT 1' % TIMELINES.get('month')))
    month_race = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[21::2])), DB_TABLE_NAME, 'WHERE id >= %s' % month_id)

    lastMonth_worksheet_back_win.append(BACK_WIN_XLSX_COLUMNS)

    for row in month_race:
        lastMonth_worksheet_back_win.append(row)
    lastMonth_workbook_back_win.save(PATH + '/XLSX/LAST_MONTH/lastMonthRacesBackWin.xlsx')


    ####################################################################################################
    ################################ LAST MONTH RACES LAY WIN INFORMATION ##############################
    ####################################################################################################

    lastMonth_workbook_lay_win = openpyxl.Workbook()
    lastMonth_worksheet_lay_win = lastMonth_workbook_lay_win.active
    month_race = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[22::2])), DB_TABLE_NAME, 'WHERE id >= %s' % month_id)

    lastMonth_worksheet_lay_win.append(LAY_WIN_XLSX_COLUMNS)

    for row in month_race:
        lastMonth_worksheet_lay_win.append(row)
    lastMonth_workbook_lay_win.save(PATH + '/XLSX/LAST_MONTH/lastMonthRacesLayWin.xlsx')


def db_to_xslx_alltime():
    ####################################################################################################
    ################################ ALL TIME RACES GENERAL INFORMATION ################################
    ####################################################################################################

    allTime_workbook_general = openpyxl.Workbook()
    allTime_worksheet_general = allTime_workbook_general.active
    allTime_race_general = select(','.join(DB_COLUMS[:19]), DB_TABLE_NAME)

    allTime_worksheet_general.append(GENERAL_XLSX_COLUMNS)

    for row in allTime_race_general:
        allTime_worksheet_general.append(row)
    allTime_workbook_general.save(PATH + '/XLSX/ALL_TIME/allTimeRacesGeneral.xlsx')


    ####################################################################################################
    ############################### ALL TIME RACES BACK WIN INFORMATION ################################
    ####################################################################################################

    allTime_workbook_back_win = openpyxl.Workbook()
    allTime_worksheet_back_win = allTime_workbook_back_win.active
    allTime_race_details = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[21::2])), DB_TABLE_NAME)

    allTime_worksheet_back_win.append(BACK_WIN_XLSX_COLUMNS)

    for row in allTime_race_details:
        allTime_worksheet_back_win.append(row)
    allTime_workbook_back_win.save(PATH + '/XLSX/ALL_TIME/allTimeRacesBackWin.xlsx')


    ####################################################################################################
    ################################ ALL TIME RACES LAY WIN INFORMATION ################################
    ####################################################################################################

    allTime_workbook_lay_win = openpyxl.Workbook()
    allTime_worksheet_lay_win = allTime_workbook_lay_win.active
    allTime_race_details = select(','.join(['Betfair_SP_Order'] + list(DB_COLUMS[22::2])), DB_TABLE_NAME)

    allTime_worksheet_lay_win.append(LAY_WIN_XLSX_COLUMNS)

    for row in allTime_race_details:
        allTime_worksheet_lay_win.append(row)
    allTime_workbook_lay_win.save(PATH + '/XLSX/ALL_TIME/allTimeRacesLayWin.xlsx')

