#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/7/13 9:39
#--RevisedDate:   
#------------------------------------

import sqlite3
import os
import sys
import datetime


def cur_file_dir():
    """To get the file root path."""
    # path = sys.path[0]
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


def create_db():
    conn = sqlite3.connect(cur_file_dir() + '\\IP_Record.db3')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS IP')
    c.execute('''
            CREATE TABLE IP (
                IP          TEXT     NOT NULL,
                Location    TEXT     NOT NULL,
                Time        DATETIME NOT NULL
            );
            ''')
    conn.commit()
    conn.close()


def record(ip,location):
    try:
        if not os.path.isfile(cur_file_dir() + '\\IP_Record.db3'):
            create_db()
        else:
            conn = sqlite3.connect(cur_file_dir() + '\\IP_Record.db3',check_same_thread = False)
            c = conn.cursor()
            c.execute('INSERT INTO IP (IP,Location,Time) VALUES (?,?,?)',[ip,location,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            conn.commit()
            conn.close()
    except:
        pass
