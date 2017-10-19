#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/18
#--RevisedDate:
#------------------------------------

import pyodbc
import common
import pandas as pd
import time
import datetime
import flask
# 目前存在的问题
# 1.connection_string的引入的问题
# 2.


# 读取SQL代码
with open(common.sql_path + '\\DocTracking_cutting_code.sql', 'r') as cutting_code:
    cutter_code = cutting_code.read()

with open(common.cur_file_dir()+'\\sql\\DocTracking_first_mapper_code.sql', 'r') as first_mapping_code:
    first_mapper_code = first_mapping_code.read()

with open(common.cur_file_dir()+'\\sql\\DocTracking_last_mapper_code.sql', 'r') as last_mapping_code:
    last_mapper_code = last_mapping_code.read()

with open(common.cur_file_dir()+'\\sql\\DocTracking_charting_code.sql', 'r') as charting_code:
    charter_code = charting_code.read()

with open(common.cur_file_dir()+'\\sql\\DocTracking_link_code.sql', 'r') as link_code:
    linker_code = link_code.read()


def get_processid(docid):
    connection_string = 'Driver={SQL Server};Server=' + common.sql_server + ';Database=' + common.sql_database + ';Uid=' + common.sql_user + ';Pwd=' + common.sql_pw + ';Trusted_Domain=msdomain1;Trusted_Connection=1;'
    code = '''
        select ProcessId
        from DocumentAcquisition..MasterProcess
        where DocumentId=%s
        ''' % (docid)
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    processid = cursor.execute(code).fetchall()[0][0]
    return processid


def get_log(connection_string, processid, timediff):
    connection = pyodbc.connect(connection_string)
    cursor = connection.cursor()
    # 获取SQL运行的结果
    # cutter information
    cutting = cursor.execute(cutter_code % (timediff, processid)).fetchall()
    if len(cutting) != 0:
        cutter = cutting[0][0]
        cutter_time = cutting[0][1]
    else:
        cutter = ''
        cutter_time = ''

    # first mapper information
    first_mapping = cursor.execute(first_mapper_code % (timediff, processid)).fetchall()
    if len(first_mapping) != 0:
        first_mapper = first_mapping[0][0]
        first_mapper_time = first_mapping[0][1]
    else:
        first_mapper = ''
        first_mapper_time = ''

    # last mapper information
    last_mapping = cursor.execute(last_mapper_code % (timediff, processid)).fetchall()
    if len(last_mapping) !=0:
        last_mapper = last_mapping[0][0]
        last_mapper_time = last_mapping[0][1]
    else:
        last_mapper = ''
        last_mapper_time = ''

    # charter information
    charting = cursor.execute(charter_code % (timediff, processid)).fetchall()
    if len(charting) != 0:
        charter = charting[0][0]
        charter_time = charting[0][1]
    else:
        charter = ''
        charter_time = ''

    # linker information
    linking = cursor.execute(linker_code % (timediff, processid)).fetchall()
    if len(linking) != 0:
        linker = linking[0][0]
        linker_time = linking[0][1]
    else:
        linker = ''
        linker_time = ''

    cutting_list = [cutter, cutter_time]
    first_mapping_list = [first_mapper, first_mapper_time]
    last_mapping_list = [last_mapper, last_mapper_time]
    charting_list = [charter, charter_time]
    linking_list = [linker, linker_time]
    log_list = [cutting_list, first_mapping_list, last_mapping_list, charting_list, linking_list]

    record_list = []
    for each in log_list:
        if log_list.index(each) == 0:# 对于cutting
            if len(cutter) != 0:# 以后可以多增加内容，目前暂时只有creation date，operation和user
                record = [str(1), each[1].strftime('%Y-%m-%d %H:%M:%S'), 'Cutting', each[0]]
                record_list.append(record)
            else:
                record = [str(1), '', 'No Cutting', '']
                record_list.append(record)

        elif log_list.index(each) == 1:
            if len(first_mapper) != 0:
                record = [str(2), each[1].strftime('%Y-%m-%d %H:%M:%S'), 'First Mapping', each[0]]
                record_list.append(record)
            else:
                record = [str(2), '', 'No Mapping', '']
                record_list.append(record)

        elif log_list.index(each) == 2:
            if len(last_mapper) != 0:
                record = [str(3),  each[1].strftime('%Y-%m-%d %H:%M:%S'), 'Last Mapping', each[0]]
                record_list.append(record)
            else:
                record = [str(3), '', 'No Mapping', '']
                record_list.append(record)

        elif log_list.index(each) == 3:
            if len(charter) != 0:
                record = [str(4), each[1].strftime('%Y-%m-%d %H:%M:%S'), 'Add Chart', each[0]]
                record_list.append(record)
            else:
                record = [str(4), '', 'No Need Chart', '']
                record_list.append(record)

        else:
            if len(linker) != 0:
                record = [str(5), each[1].strftime('%Y-%m-%d %H:%M:%S'), 'Add Link', each[0]]
                record_list.append(record)
            else:
                record = [str(5), '', 'No Need Link', '']
                record_list.append(record)

    return record_list


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


def run(processid, timediff):
    connection_string = 'Driver={SQL Server};Server=' + common.sql_server + ';Database=' + common.sql_database + ';Uid=' + common.sql_user + ';Pwd=' + common.sql_pw + ';Trusted_Domain=msdomain1;Trusted_Connection=1;'
    total_result = get_log(connection_string, processid, timediff)
    pd_result = pd.DataFrame(total_result, columns=['No', 'Operation Time', 'Operation', 'User'])
    pd.set_option('display.max_colwidth', -1)
    html_code = pd_result.to_html(classes='tablestyle', index=False)
    html_code = css_code + html_code
    return html_code
