#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 11:01
#--RevisedDate:   
#------------------------------------

import os
import sys


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


def init():
    if not os.path.exists(sql_path):
        os.makedirs(sql_path)