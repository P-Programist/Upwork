import datetime as dt
import openpyxl

from settings import (
    PATH,
    DB_COLUMS,
    DB_TABLE_NAME,
    GENERAL_XLSX_COLUMNS,
    BACK_LAY_XLSX_COLUMNS,
    CONNECTION, CURSOR,
    FILTER_RACE, FILTER_DISTANCE
)

INSERT_COLUMNS_ROW = ', '.join(DB_COLUMS)


def select(column_name: str, table_name: str, conditions: str = None):
    if conditions:
        sql = "SELECT %s FROM %s %s;" % (column_name, table_name, conditions)
    else:
        sql = "SELECT %s FROM %s;" % (column_name, table_name)

    result = CURSOR.execute(sql)
    rows = result.fetchall()

    return tuple(rows)


def data_uploader(data=None):
    CURSOR.executemany("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
        DB_TABLE_NAME, INSERT_COLUMNS_ROW), data)
    CONNECTION.commit()


####################################################################################################
################################## TODAY RACES GENERAL INFORMATION #################################
####################################################################################################
def get_period_information(xlsx_header_data):
    '''
    The function might either accept or not a list with race's dates.
    Then the accepted data will be substituted at the top of XLSX file to show which races were for that specific period of time.
    '''
    one_month_race_time = []
    three_months_race_time = []
    last_year_race_time = []

    LAST_MONTH = dt.datetime.strftime(
        (dt.datetime.today() - dt.timedelta(days=31)), '%-d/%-m/%y')
    LAST_THREE_MONTHS = dt.datetime.strftime(
        (dt.datetime.today() - dt.timedelta(days=90)), '%-d/%-m/%y')
    LAST_YEAR = dt.datetime.strftime(
        (dt.datetime.today() - dt.timedelta(days=365)), '%-d/%-m/%y')

    one_month_min_id = select(
        'MIN(id)',
        DB_TABLE_NAME,
        'WHERE date = \'%s\'' % LAST_MONTH
    )

    three_month_min_id = select(
        'MIN(id)',
        DB_TABLE_NAME,
        'WHERE date = \'%s\'' % LAST_THREE_MONTHS
    )

    last_year_min_id = select(
        'MIN(id)',
        DB_TABLE_NAME,
        'WHERE date = \'%s\'' % LAST_YEAR
    )

    for year_list, period_id in ((one_month_race_time, one_month_min_id), (three_months_race_time, three_month_min_id), (last_year_race_time, last_year_min_id)):
        for header_race_type in xlsx_header_data:
            race = header_race_type[-2]

            if len(period_id) > 0:
                if len(period_id[0]) > 0:
                    if period_id[0][0]:
                        sql = '''WHERE id >= \'%s\'
                            AND race_type = \'%s\'
                            GROUP BY date, time, race_type
                            ORDER BY time, race_type''' % (period_id[0][0], race)

                        if not three_months_race_time:
                            sql = '''WHERE id >= \'%s\'
                                AND race_type = \'%s\'
                                GROUP BY date, time, race_type
                                ORDER BY time, race_type''' % (int(period_id[0][0]) + 3, race)

                            if FILTER_RACE:
                                sql = '''WHERE id >= \'%s\'
                                    AND race_type = \'%s\'
                                    GROUP BY date, time, race_type
                                    ORDER BY time, race_type''' % (int(period_id[0][0]) + 3, FILTER_RACE)

                                if FILTER_DISTANCE:
                                    sql = '''WHERE id >= \'%s\'
                                        AND race_type = \'%s\'
                                        AND distance = \'%s\'
                                        GROUP BY date, time, race_type
                                        ORDER BY time, race_type''' % (int(period_id[0][0]) + 3, FILTER_RACE, FILTER_DISTANCE)

                            if FILTER_DISTANCE:
                                sql = '''WHERE id >= \'%s\'
                                    AND distance = \'%s\'
                                    GROUP BY date, time, race_type
                                    ORDER BY time, race_type''' % (int(period_id[0][0]) + 3, FILTER_DISTANCE)
                        else:
                            if FILTER_RACE:
                                sql = '''WHERE id >= \'%s\'
                                    AND race_type = \'%s\'
                                    GROUP BY date, time, race_type
                                    ORDER BY time, race_type''' % (period_id[0][0], FILTER_RACE)

                                if FILTER_DISTANCE:
                                    sql = '''WHERE id >= \'%s\'
                                        AND race_type = \'%s\'
                                        AND distance = \'%s\'
                                        GROUP BY date, time, race_type
                                        ORDER BY time, race_type''' % (period_id[0][0], FILTER_RACE, FILTER_DISTANCE)

                            if FILTER_DISTANCE:
                                sql = '''WHERE id >= \'%s\'
                                    AND distance = \'%s\'
                                    GROUP BY date, time, race_type
                                    ORDER BY time, race_type''' % (period_id[0][0], FILTER_DISTANCE)

                        year_list.extend(
                            select('date, time, race_type', DB_TABLE_NAME, sql)
                        )
                else:
                    sql = '''WHERE id >= (SELECT MIN(id) FROM races)
                        AND race_type = \'%s\'
                        GROUP BY date, time, race_type
                        ORDER BY time, race_type''' % race

                    if FILTER_RACE:
                        sql = '''WHERE id >= (SELECT MIN(id) FROM races)
                            AND race_type = \'%s\'
                            GROUP BY date, time, race_type
                            ORDER BY time, race_type''' % FILTER_RACE

                        if FILTER_DISTANCE:
                            sql = '''WHERE id >= (SELECT MIN(id) FROM races)
                                AND race_type = \'%s\'
                                AND distance = \'%s\'
                                GROUP BY date, time, race_type
                                ORDER BY time, race_type''' % (FILTER_RACE, FILTER_DISTANCE)

                    if FILTER_DISTANCE:
                        sql = '''WHERE id >= (SELECT MIN(id) FROM races)
                            AND distance = \'%s\'
                            GROUP BY date, time, race_type
                            ORDER BY time, race_type''' % FILTER_DISTANCE

                    year_list.extend(
                        select('date, time, race_type', DB_TABLE_NAME, sql))

    timelines_data = {
        "one_month": (
            "OneMonthRaces",
            set(row for row in one_month_race_time),
        ),
        "three_months": (
            "ThreeMonthsRaces",
            set(row for row in three_months_race_time),
        ),
        "year": (
            "LastYearRaces",
            set(row for row in last_year_race_time),
        )
    }

    return timelines_data


def db_to_xslx(xlsx_header_data=[]):
    timelines = get_period_information(xlsx_header_data)

    for timeline in timelines:
        workbook_general = openpyxl.Workbook()
        worksheet_general = workbook_general.active

        worksheet_general.append(GENERAL_XLSX_COLUMNS)

        filename = timelines.get(timeline)[0]
        date_and_race = timelines.get(timeline)[1]

        for header in xlsx_header_data:
            worksheet_general.append(header)

        for _ in range(4):
            worksheet_general.append(['' for _ in range(12)])

        race_data = {}
        for date, time, race_type in date_and_race:
            one_race_data = tuple(select(','.join(DB_COLUMS), DB_TABLE_NAME,
                                         'WHERE date = \'%s\' AND time = \'%s\' AND race_type = \'%s\' ORDER BY race_type, id' % (date, time, race_type)))

            for count, line in enumerate(one_race_data, 1):
                if not race_data.get(line[4]):
                    race_data[line[4]] = {}

                if not race_data.get(line[4]).get(count):
                    race_data.get(line[4])[count] = {}

                if not race_data.get(line[4])[count]:
                    if str(line[5]) == '1':
                        race_data.get(line[4])[count]["Winners"] = 1
                        race_data.get(line[4])[count]["Lost_Races"] = 0

                        race_data.get(line[4])[count]["Back_Win"] = (
                            line[12] - 1) * 1
                        race_data.get(line[4])[
                            count]["Lay_Win"] = -(line[12] - 1) * 1

                        race_data.get(line[4])[count]["Back_ROI"] = (
                            line[12] - 1) * 1
                        race_data.get(line[4])[
                            count]["Lay_ROI"] = -(line[12] - 1) * 1

                        race_data.get(line[4])[count]["Back_S_Rate"] = 100
                        race_data.get(line[4])[count]["Lay_S_Rate"] = 0

                        race_data.get(line[4])[count]["BackProbability"] = 100

                    else:
                        race_data.get(line[4])[count]["Winners"] = 0
                        race_data.get(line[4])[count]["Lost_Races"] = 1

                        race_data.get(line[4])[count]["Back_Win"] = -1
                        race_data.get(line[4])[count]["Lay_Win"] = 1

                        race_data.get(line[4])[count]["Back_ROI"] = -1
                        race_data.get(line[4])[count]["Lay_ROI"] = 1

                        race_data.get(line[4])[count]["Back_S_Rate"] = 0
                        race_data.get(line[4])[count]["Lay_S_Rate"] = 100

                        race_data.get(line[4])[count]["BackProbability"] = 0

                else:
                    if str(line[5]) == '1':
                        winners = race_data.get(line[4])[count]["Winners"]
                        lost_race = race_data.get(line[4])[count]["Lost_Races"]

                        race_data.get(line[4])[count]["Winners"] = winners + 1
                        race_data.get(line[4])[count]["Back_Win"] = (
                            line[12] - 1) * 1  # ???
                        race_data.get(line[4])[
                            count]["Lay_Win"] = -(line[12] - 1) * 1
                        race_data.get(line[4])[count]["Back_ROI"] = (
                            (line[12] - 1) * 1) / (winners + 1)
                        race_data.get(line[4])[count]["Back_S_Rate"] = round(
                            (winners + 1) / ((winners + 1) + lost_race) * 100, 3)
                        race_data.get(line[4])[count]["BackProbability"] = round(
                            (winners + 1) / ((winners + 1) + lost_race) * 100, 3)

                    else:
                        winners = race_data.get(line[4])[count]["Winners"]
                        lost_race = race_data.get(line[4])[count]["Lost_Races"]
                        back_win = race_data.get(line[4])[count]["Back_Win"]
                        lay_win = race_data.get(line[4])[count]["Lay_Win"]

                        race_data.get(line[4])[
                            count]["Lost_Races"] = lost_race + 1
                        race_data.get(line[4])[
                            count]["Back_Win"] = back_win - 1  # ???
                        race_data.get(line[4])[count]["Lay_Win"] = lay_win + 1
                        race_data.get(line[4])[count]["Lay_ROI"] = round(
                            (lay_win + 1) / (lost_race + 1), 3)
                        race_data.get(line[4])[count]["Lay_S_Rate"] = round(
                            (lost_race + 1) / ((winners) + lost_race + 1) * 100, 3)

        for race_type, race_values in race_data.items():
            worksheet_general.append(
                ['', '', '', '', '', '', '', race_type])
            worksheet_general.append(BACK_LAY_XLSX_COLUMNS)

            for bsp, data in race_values.items():
                values = list(data.values())
                back_values = values[0::2]
                lay_values = values[1::2]

                row = [bsp, int(back_values[0]) + int(lay_values[0])]
                row.extend(back_values)
                row.append('')
                row.append(bsp)
                row.extend(lay_values)

                worksheet_general.append(row)

            for _ in range(4):
                worksheet_general.append(['' for _ in range(12)])

        workbook_general.save(PATH + '/XLSX/%s.xlsx' % filename)
