#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 11:01
#--RevisedDate:   2017/10/25
#------------------------------------

import os
import sys
import IPTracking
import Web_API


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
connection_string_multithread = 'Driver={SQL Server Native Client 10.0};Server=' + sql_server + ';Database=' + sql_database + ';Uid=' + sql_user + ';Pwd=' + sql_pw + ';Trusted_Domain=msdomain1;Trusted_Connection=yes;MARS_Connection=yes;'
DB_path = cur_file_dir() + '\\Database\\'
IP_Tracking_DB_file_path = DB_path + 'IP_Tracking.db3'
Operation_Tracking_DB_file_path = DB_path + 'Operation_Tracking.db3'

stickers_path = cur_file_dir() + '\\static\\images\\stickers\\'
apps_path = cur_file_dir() + '\\apps\\'
temp_path = cur_file_dir() + '\\temp\\'


def init():
    if not os.path.exists(sql_path):
        os.makedirs(sql_path)
    if not os.path.exists(DB_path):
        os.makedirs(DB_path)
    if not os.path.exists(stickers_path):
        os.makedirs(stickers_path)
    if not os.path.exists(apps_path):
        os.makedirs(apps_path)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    if not os.path.isfile(IP_Tracking_DB_file_path):
        IPTracking.create_db(IP_Tracking_DB_file_path)
    if not os.path.isfile(Operation_Tracking_DB_file_path):
        Web_API.create_db(Operation_Tracking_DB_file_path)


def get_IP(user_request):
    try:
        _ip = user_request.headers["X-Real-IP"]
        if _ip is not None:
            return _ip
    except:
        return user_request.remote_addr
