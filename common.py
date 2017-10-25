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


domain = 'http://szvm20152'
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

css_code = '''
    <style>
    .tablestyle table {
        width:100%;
        margin:15px 0
    }
    .tablestyle th {
        background-color:#87CEFA;
        background:-o-linear-gradient(90deg, #87CEFA, #bae3fc);
        background:-moz-linear-gradient( center top, #87CEFA 5%, #bae3fc 100% );
        background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #87CEFA), color-stop(1, #bae3fc) );
        filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#87CEFA', endColorstr='#bae3fc');
        color:#000000
    }
    .tablestyle,.tablestyle th,.tablestyle td
    {
        font-size:0.95em;
        text-align:left;
        padding:4px;
        border:1px solid #5fbdf8;
        border-collapse:collapse
    }
    .tablestyle td {

        border:1px solid #bae3fc;
        border-collapse:collapse
    }
    .tablestyle tr:nth-child(odd){
        background-color:#d7eefd;
        background:-o-linear-gradient(90deg, #d7eefd, #f7fbfe);
        background:-moz-linear-gradient( center top, #d7eefd 5%, #f7fbfe 100% );
        background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #d7eefd), color-stop(1, #f7fbfe) );
        filter:progid:DXImageTransform.Microsoft.gradient(startColorstr='#d7eefd', endColorstr='#f7fbfe');
    }
    .tablestyle tr:nth-child(even){
        background-color:#fdfdfd;
    }
    </style>
'''


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
