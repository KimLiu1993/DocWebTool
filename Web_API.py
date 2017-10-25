#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/25 8:39
#--RevisedDate:   
#------------------------------------

import sqlite3
import datetime
import DAP_API as dap
import common

userid = 601 # Franklin Lai


def create_db(Operation_Tracking_DB_file_path):
    conn = sqlite3.connect(Operation_Tracking_DB_file_path, check_same_thread=False)
    conn.cursor().execute('DROP TABLE IF EXISTS OperationTracking')
    conn.cursor().execute('''
                        CREATE TABLE OperationTracking (
                            IP          TEXT     NOT NULL,
                            Operation   TEXT     NOT NULL,
                            Comment     TEXT     NOT NULL,
                            Time        DATETIME NOT NULL
                        );
                        ''')
    conn.commit()
    conn.close()


def mapping(user_request, processid, secid):
    ip = common.get_IP(user_request)
    return_info = dap.add_mapping(userid, processid, secid)
    try:
        conn = sqlite3.connect(common.Operation_Tracking_DB_file_path, check_same_thread=False)
        conn.cursor().execute('INSERT INTO OperationTracking (IP, Operation, Comment, Time) VALUES (?, ?, ?, ?)', [ip, 'AddMapping', 'Add ' + str(secid) + ' to ' + str(processid), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        conn.commit()
        conn.close()

        if return_info['success'] is True:
            return 'Done!'
        else:
            return 'Sorry, failed!'
    except:
        return 'Sorry, failed!'


def import_doc_mapping(user_request, from_processid, to_processid):
    ip = common.get_IP(user_request)
    return_info = dap.import_doc_mapping(userid, to_processid, from_processid)
    try:
        conn = sqlite3.connect(common.Operation_Tracking_DB_file_path, check_same_thread=False)
        conn.cursor().execute('INSERT INTO OperationTracking (IP, Operation, Comment, Time) VALUES (?, ?, ?, ?)', [ip, 'ImportDocMapping', 'Import from ' + str(from_processid) + ' to ' + str(to_processid), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        conn.commit()
        conn.close()
        return 'Done!'
    except:
        return 'Sorry, failed!'