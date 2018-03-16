#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/18
#--RevisedDate:   2017/10/27
#--RevisedDate:   2018/03/12 
#------------------------------------


import datetime
import pyodbc
import common
import pandas as pd


# 读取SQL代码
with open(common.sql_path + '\\DocTracking.sql', 'r') as tracking:
    tracking_code = tracking.read()


def get_processid(docid):
    url = 'http://dcweb613/GED/Sec/findSECFundDocumentList.action?form.category=&form.docType=&form.status=&form.format=&form.filingId=&form.processId=&form.documentId=' + str(docid) + '&form.formType=&form.accessionNumber=&form.cik=&form.from=&form.to=&form.cusip=&form.companyName=&form.investmentId=&form.specialStatus=0&form.policyId='
    req = requests.get(url, timeout=300).json()
    process_id = req['metaData']['rows'][0]['processId']
    return process_id


def get_log(connection, processid, timediff):

    cursor = connection.cursor()
    log_list = pd.read_sql(tracking_code % (timediff, processid), connection)
    log_list = log_list.values.tolist()

    row = 0
    record_list = []
    for each in log_list:
        row = row + 1
        if row == 1:
            record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'Cutting']
            record_list.append(record)
            
        elif each[2] != log_list[row-2][2]:
            record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'Doctype changed']
            record_list.append(record)

        elif each[4] != log_list[row-2][4]:
            record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'EffDate changed']
            record_list.append(record)

        elif each[5] != log_list[row-2][5]:
            if log_list[row-2][5] is None:
                record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'First mapping']
                record_list.append(record)
            else:
                record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'Mapping changed']
                record_list.append(record)
        elif each[6] != log_list[row-2][6]:
            record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), 'Content changed']
            record_list.append(record)
        else:
            record = [str(row), each[0], each[1], each[2], each[4], each[7], each[8].strftime('%Y-%m-%d %H:%M:%S'), '']
            record_list.append(record)
    cursor.close()
    return record_list
    


def run(processid, timediff):
    connection = pyodbc.connect(common.connection_string_multithread)
    result_list = get_log(connection, processid, timediff)
    result = pd.DataFrame(result_list, columns=['No', 'ProcessId', 'DocumentId', 'DocType', 'EffectiveDate', 'User', 'OperationTime', 'Comment'])
    pd.set_option('display.max_colwidth', -1)
    html_code = result.to_html(classes='tablestyle', index=False)
    html_code = common.css_code + html_code
    return html_code

# processid = 54677854
# timediff = 13
# a = run(processid, timediff)
# print(a)

# 读取SQL代码
# with open(common.sql_path + '\\DocTracking_cutting_code.sql', 'r') as cutting_code:
#     cutter_code = cutting_code.read()

# with open(common.cur_file_dir()+'\\sql\\DocTracking_first_mapper_code.sql', 'r') as first_mapping_code:
#     first_mapper_code = first_mapping_code.read()

# with open(common.cur_file_dir()+'\\sql\\DocTracking_last_mapper_code.sql', 'r') as last_mapping_code:
#     last_mapper_code = last_mapping_code.read()

# with open(common.cur_file_dir()+'\\sql\\DocTracking_charting_code.sql', 'r') as charting_code:
#     charter_code = charting_code.read()

# with open(common.cur_file_dir()+'\\sql\\DocTracking_link_code.sql', 'r') as link_code:
#     linker_code = link_code.read()


# def get_processid(docid):
#     connection = pyodbc.connect(common.connection_string_multithread)
#     code = '''
#         select ProcessId
#         from DocumentAcquisition..MasterProcess
#         where DocumentId=%s
#         ''' % (docid)
#     cursor = connection.cursor()
#     processid = cursor.execute(code).fetchall()[0][0]
#     cursor.close()
#     connection.close()
#     return processid


# def get_log(connection, processid, timediff):
#     cursor = connection.cursor()
#     # 获取SQL运行的结果
#     # cutter information
#     cutting = cursor.execute(cutter_code % (timediff, processid)).fetchall()
#     if len(cutting) != 0:
#         cutter = cutting[0][0]
#         cutter_time = cutting[0][1]
#     else:
#         cutter = ''
#         cutter_time = ''

#     # first mapper information
#     first_mapping = cursor.execute(first_mapper_code % (timediff, processid)).fetchall()
#     if len(first_mapping) != 0:
#         first_mapper = first_mapping[0][0]
#         first_mapper_time = first_mapping[0][1]
#     else:
#         first_mapper = ''
#         first_mapper_time = ''

#     # last mapper information
#     last_mapping = cursor.execute(last_mapper_code % (timediff, processid)).fetchall()
#     if len(last_mapping) !=0:
#         last_mapper = last_mapping[0][0]
#         last_mapper_time = last_mapping[0][1]
#     else:
#         last_mapper = ''
#         last_mapper_time = ''

#     # charter information
#     charting = cursor.execute(charter_code % (timediff, processid)).fetchall()
#     if len(charting) != 0:
#         charter = charting[0][0]
#         charter_time = charting[0][1]
#     else:
#         charter = ''
#         charter_time = ''

#     # linker information
#     linking = cursor.execute(linker_code % (timediff, processid)).fetchall()
#     if len(linking) != 0:
#         linker = linking[0][0]
#         linker_time = linking[0][1]
#     else:
#         linker = ''
#         linker_time = ''

#     record_list = []
#     if len(cutter) != 0:
#         cutting_list = [str(1), processid, cutter_time.strftime('%Y-%m-%d %H:%M:%S'), 'Cutting', cutter]
#         record_list.append(cutting_list)
#     else:
#         cutting_list = ['', '', '', 'No Cutting', '']
#         record_list.append(cutting_list)

#     if len(first_mapper) != 0:
#         first_mapping_list = [str(2), processid, first_mapper_time.strftime('%Y-%m-%d %H:%M:%S'), 'First Mapping', first_mapper]
#         record_list.append(first_mapping_list)
#     else:
#         first_mapping_list = ['', '', '', 'No Mapping', '']
#         record_list.append(first_mapping_list)

#     if len(last_mapper) != 0:
#         if len(first_mapper) != 0:
#             last_mapping_list = [str(3), processid, last_mapper_time.strftime('%Y-%m-%d %H:%M:%S'), 'Last Mapping', last_mapper]
#             record_list.append(last_mapping_list)
#         else:
#             last_mapping_list = [str(3), processid, last_mapper_time.strftime('%Y-%m-%d %H:%M:%S'), 'Mapping is not completed.', last_mapper]
#             record_list.append(last_mapping_list)
#     else:
#         last_mapping_list = ['', '', '', 'No Mapping', '']
#         record_list.append(last_mapping_list)

#     if len(linker) != 0:
#         linking_list = [str(5), processid, linker_time.strftime('%Y-%m-%d %H:%M:%S'), 'Add Link', linker]
#         record_list.append(linking_list)
#     else:
#         linking_list = ['', '', '', 'No Link', '']
#         record_list.append(linking_list)
    
#     if len(charter) != 0:
#         charting_list = [str(4), processid, charter_time.strftime('%Y-%m-%d %H:%M:%S'), 'Add Chart', charter]
#         record_list.append(charting_list)
#     else:
#         charting_list = ['', '', '', 'No Chart', '']
#         record_list.append(charting_list)

#     cursor.close()
#     return record_list


# def run(processid, timediff):
#     connection = pyodbc.connect(common.connection_string_multithread)
#     total_result = get_log(connection, processid, timediff)
#     pd_result = pd.DataFrame(total_result, columns=['No', 'Processid', 'Operation Time', 'Operation', 'User'])
#     pd.set_option('display.max_colwidth', -1)
#     html_code = pd_result.to_html(classes='tablestyle', index=False)
#     html_code = '<p>ProcessId: ' + str(processid) + '</p>' + common.css_code + html_code
#     connection.close()
#     return html_code
