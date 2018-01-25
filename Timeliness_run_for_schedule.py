#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2018/1/4 10:48
#--RevisedDate:   2018/1/17
#------------------------------------

import sys
import sqlite3
import pyodbc
import common


def create_db(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS MFTimeliness')
    # c.execute('DROP TABLE IF EXISTS VATimeliness')
    c.execute('DROP TABLE IF EXISTS UITTimeliness')
    with open(common.sql_path + '\\MFTimeliness_Create_DB.sql', encoding='UTF-8') as code_reader1:
        code1 = code_reader1.read()
    # with open(common.sql_path + '\\MFTimeliness_Create_Index.sql', encoding='UTF-8') as code_reader2:
    #     code2 = code_reader2.read()
    with open(common.sql_path + '\\VATimeliness_Create_DB.sql', encoding='UTF-8') as code_reader3:
        code3 = code_reader3.read()
    # with open(common.sql_path + '\\VATimeliness_Create_Index.sql', encoding='UTF-8') as code_reader4:
    #     code4 = code_reader4.read()
    with open(common.sql_path + '\\UITTimeliness_Create_DB.sql', encoding='UTF-8') as code_reader5:
        code5 = code_reader5.read()
    # with open(common.sql_path + '\\UITTimeliness_Create_Index.sql', encoding='UTF-8') as code_reader6:
    #     code6 = code_reader6.read()
    c.execute(code1)
    # c.execute(code2)
    c.execute(code3)
    # c.execute(code4)
    c.execute(code5)
    # c.execute(code6)
    c.close()
    conn.commit()
    conn.close()


def read_from_sql(sql_path):
    connection = pyodbc.connect(common.connection_string_multithread)
    with open(sql_path, encoding='UTF-8') as code_reader:
        code = code_reader.read()
    cursor = connection.cursor()
    cursor.execute(code)
    detail_list = cursor.fetchall()
    connection.close()
    return detail_list


def input_to_sqlite3(db_path, data, process):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    if process == 'MF':
        try:
            c.executemany('insert into MFTimeliness values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
        except:
            for item in data:
                try:
                    c.execute('insert into MFTimeliness values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', item)
                except sqlite3.IntegrityError:
                    pass
    elif process == 'VA':
        for item in data:
            try:
                c.execute('insert into VATimeliness values (?,?,?,?,?,?,?,?,?,?,?,?)', item)
            except sqlite3.IntegrityError:
                pass
    elif process == 'UIT':
        try:
            c.executemany('insert into UITTimeliness values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', data)
        except:
            for item in data:
                try:
                    c.execute('insert into UITTimeliness values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', item)
                except sqlite3.IntegrityError:
                    pass
    c.close()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    try:
        print('Reading Timeliness data from database...')
        MF_pd_sql_data = read_from_sql(common.sql_path + '\\MFTimeliness.sql')
        VA_pd_sql_data = read_from_sql(common.sql_path + '\\VATimeliness.sql')
        UIT_pd_sql_data = read_from_sql(common.sql_path + '\\UITTimeliness.sql')
    except Exception as e:
        print('Error: ' + str(e))
        sys.exit()

    print('Writing data into database...')
    create_db(common.Timeliness_DB_path)
    input_to_sqlite3(common.Timeliness_DB_path, MF_pd_sql_data, 'MF')
    input_to_sqlite3(common.Timeliness_DB_path, VA_pd_sql_data, 'VA')
    input_to_sqlite3(common.Timeliness_DB_path, UIT_pd_sql_data, 'UIT')

    print('Done!')
    sys.exit()