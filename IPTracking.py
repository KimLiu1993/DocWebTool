#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/17 16:56
#--RevisedDate:   
#------------------------------------

import sqlite3
import datetime
import common


def get_IP(user_request):
    try:
        _ip = user_request.headers["X-Real-IP"]
        if _ip is not None:
            return _ip
    except:
        return user_request.remote_addr


def create_db(IP_Tracking_DB_path):
    conn = sqlite3.connect(IP_Tracking_DB_path, check_same_thread=False)
    conn.cursor().execute('DROP TABLE IF EXISTS IP')
    conn.cursor().execute('''
                        CREATE TABLE IP (
                            IP          TEXT     NOT NULL,
                            Location    TEXT     NOT NULL,
                            Time        DATETIME NOT NULL
                        );
                        ''')
    conn.commit()
    conn.close()


def log_IP(user_request, location):
    ip = get_IP(user_request)
    try:
        conn = sqlite3.connect(common.IP_Tracking_DB_path, check_same_thread=False)
        conn.cursor().execute('INSERT INTO IP (IP, Location, Time) VALUES (?, ?, ?)', [ip, str(location), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        conn.commit()
        conn.close()
    except:
        pass