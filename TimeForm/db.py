import os
import csv
import sqlite3
from settings import PATH, DB_COLUMS, pathlib, CREATE_RACE_RESULT_TABLE_QUERY, DB_PATH


CONNECTION = sqlite3.connect(DB_PATH)
CURSOR = CONNECTION.cursor()


INSERT_COLUMNS_ROW = ', '.join(DB_COLUMS)



def upload_csv(csv_file):
    reader = csv.reader(csv_file)
    try:
        next(reader)
        return reader
    except StopIteration:
        return 0


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


def insert(table_name, columns, race_types, data=None):
    current_date = None
    if data:
        for row in data:

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
                    CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
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

                CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
                        table_name, columns), row)

                CONNECTION.commit()
            current_date = race_date

        


def select(column_name, table_name, conditions=None):
    if conditions:
        sql = "SELECT %s FROM %s %s;" % (column_name, table_name, conditions)
    else:
        sql = "SELECT %s FROM %s;" % (column_name, table_name)

    result = CURSOR.execute(sql)
    return result.fetchall()


def main():
    drop_table('race_results')
    create('race_results')

    if CSV_DATA:
        csv_file = open(PATH + '/csv_data/data.csv')
        csv_reader = upload_csv(csv_file)

        race_types = [name[0] for name in select('race_type', 'race_results')]
        insert('race_results', INSERT_COLUMNS_ROW, race_types, csv_reader)

        csv_file.close()

    CURSOR.close()

if __name__ == "__main__":
    main()

    
