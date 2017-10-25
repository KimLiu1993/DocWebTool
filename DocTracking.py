#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/18
#--RevisedDate:   2017/10/24
#------------------------------------

import pyodbc
import common
import pandas as pd


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
    connection = pyodbc.connect(common.connection_string_multithread)
    code = '''
        select ProcessId
        from DocumentAcquisition..MasterProcess
        where DocumentId=%s
        ''' % (docid)
    cursor = connection.cursor()
    processid = cursor.execute(code).fetchall()[0][0]
    cursor.close()
    connection.close()
    return processid


def get_log(connection, processid, timediff):
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

    record_list = []
    if len(cutter) != 0:
        cutting_list = [str(1), processid, cutter_time.strftime('%Y-%m-%d %H:%M:%S'), 'Cutting', cutter]
        record_list.append(cutting_list)
    else:
        cutting_list = ['', '', '', 'No Cutting', '']
        record_list.append(cutting_list)

    if len(first_mapper) != 0:
        first_mapping_list = [str(2), processid, first_mapper_time.strftime('%Y-%m-%d %H:%M:%S'), 'First Mapping', first_mapper]
        record_list.append(first_mapping_list)
    else:
        first_mapping_list = ['', '', '', 'No Mapping', '']
        record_list.append(first_mapping_listrecord)

    if len(last_mapper) != 0:
        last_mapping_list = [str(3), processid, last_mapper_time.strftime('%Y-%m-%d %H:%M:%S'), 'Last Mapping', last_mapper]
        record_list.append(last_mapping_list)
    else:
        last_mapping_list = ['', '', '', 'No Mapping', '']
        record_list.append(last_mapping_list)

    if len(linker) != 0:
        linking_list = [str(5), processid, linker_time.strftime('%Y-%m-%d %H:%M:%S'), 'Add Link', linker]
        record_list.append(linking_list)
    else:
        linking_list = ['', '', '', 'No Link', '']
        record_list.append(linking_list)
    
    if len(charter) != 0:
        charting_list = [str(4), processid, charter_time.strftime('%Y-%m-%d %H:%M:%S'), 'Add Chart', charter]
        record_list.append(charting_list)
    else:
        charting_list = ['', '', '', 'No Chart', '']
        record_list.append(charting_list)

    cursor.close()
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
    connection = pyodbc.connect(common.connection_string_multithread)
    total_result = get_log(connection, processid, timediff)
    pd_result = pd.DataFrame(total_result, columns=['No', 'Processid', 'Operation Time', 'Operation', 'User'])
    pd.set_option('display.max_colwidth', -1)
    html_code = pd_result.to_html(classes='tablestyle', index=False)
    html_code = css_code + html_code
    connection.close()
    return html_code
