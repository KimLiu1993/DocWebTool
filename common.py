#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 11:01
#--RevisedDate:   2017/10/19
#------------------------------------

import os
import sys
import IPTracking


def cur_file_dir():
    """
    Get the file root path.
    """
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if os.path.isdir(path):
        return path
    elif os.path.isfile(path):
        return os.path.dirname(path)


sql_path = cur_file_dir() + '\\sql\\'
sql_server = 'dcdrdb601\dminputdb'
sql_database = 'DocumentAcquisition'
sql_user = 'jyu2'
sql_pw = 'hhh'
IP_Tracking_DB_path = cur_file_dir() + '\\Database\\'
IP_Tracking_DB_file_path = IP_Tracking_DB_path + 'IP_Tracking.db3'


def init():
    if not os.path.exists(sql_path):
        os.makedirs(sql_path)
    if not os.path.exists(IP_Tracking_DB_path):
        os.makedirs(IP_Tracking_DB_path)
    if not os.path.isfile(IP_Tracking_DB_file_path):
        IPTracking.create_db(IP_Tracking_DB_file_path)