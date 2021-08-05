import csv
import sqlite3
from static import PATH, CSV_COLUMNS

DB_PATH = PATH + '/results.db'
CONNECTION = sqlite3.connect(DB_PATH)
CURSOR = CONNECTION.cursor()

FILENAMES = (
    'data0.csv','data1.csv',
    'data2.csv','data3.csv',
    'data4.csv','data5.csv',
    'data6.csv'
)

INSERT_COLUMNS_ROW = ', '.join(CSV_COLUMNS)


CREATE_RACE_RESULT_TABLE_QUERY = '''
CREATE TABLE race_results(
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

    stake INT DEFAULT 1,
    back_winners FLOAT DEFAULT 0,
    lay_winners FLOAT DEFAULT 0,

    back_win FLOAT DEFAULT 0,
    lay_win FLOAT DEFAULT 0,

    back_roi FLOAT DEFAULT 0,
    lay_roi FLOAT DEFAULT 0,

    back_s_rate FLOAT DEFAULT 0,
    lay_s_rate FLOAT DEFAULT 0,

    back_probability FLOAT DEFAULT 0,
    number_of_races INT DEFAULT 1);'''


def upload_csv(csv_file):
    reader = csv.reader(csv_file)
    next(reader)
    return reader


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


def insert(table_name, columns, horse_names, data=None):
    if data:
        for row in data:
            horse_name = row[7]
            position = row[5]
            if horse_names:
                if horse_name in horse_names:
                    if position == '1':
                        CURSOR.execute(
                            'UPDATE %s \
                                SET back_winners = back_winners+1, \
                                    back_win = (bsp-1) * stake, \
                                        lay_win = lay_win + stake, \
                                            number_of_races=number_of_races+1  \
                                                WHERE horse_name = \'%s\';' % (table_name, horse_name.replace('\'', '"')))
                    else:
                        CURSOR.execute(
                            'UPDATE %s \
                                SET lay_winners = lay_winners+1, \
                                    back_win = back_win - stake, \
                                        lay_win = -(bsp-1) * stake, \
                                            number_of_races=number_of_races+1 \
                                                WHERE horse_name = \'%s\';' % (table_name, horse_name.replace('\'', '"')))
                else:
                    CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
                        table_name, columns), row)
            else:
                if position == '1':
                    row.extend([1, 1, 0, (float(row[12]) - 1) * 1, 1])
                else:
                    row.extend([1, 0, 1, -1, -(float(row[12]) - 1) * 1])

                updated_columns = columns + ', stake, back_winners, lay_winners, back_win, lay_win'

                CURSOR.execute("INSERT INTO %s (%s) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % (
                        table_name, updated_columns), row)
                
        CONNECTION.commit()


def select(column_name, table_name, conditions=None):
    if conditions:
        sql = "SELECT %s FROM %s %s;" % (column_name, table_name, conditions)
    else:
        sql = "SELECT %s FROM %s;" % (column_name, table_name)

    result = CURSOR.execute(sql)
    return result.fetchall()


def query(cmd):
    print(cmd)
    recs = CURSOR.execute(cmd)
    return recs.fetchall()

if __name__ == "__main__":
    # drop_table('race_results')
    # create('race_results')
    for filename in FILENAMES:
        csv_file = open(PATH + '/' + filename)

        data = upload_csv(csv_file)
        horse_names = [name[0] for name in select('horse_name', 'race_results')]
        insert('race_results', INSERT_COLUMNS_ROW, horse_names, data)
        csv_file.close()

    

    # result = select('horse_name', 'race_results',)
    # for row in result:
    #     print(row)

    CURSOR.close()
