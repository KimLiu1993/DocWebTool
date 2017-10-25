#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Sharol Liu
#--CreationDate:  2017/10/23
#--RevisedDate:
#------------------------------------


import common
import pyodbc
import pandas as pd
import math
import threading

# 读取SQL代码
with open(common.sql_path + '\\MapByDocFromCIK_GetSecIdFromFilingId.sql', 'r', encoding='UTF-8') as filingid_secid_code:
    filingid_secid_code = filingid_secid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_GetSecidFromCIK.sql', 'r', encoding='UTF-8') as cik_secid_code:
    cik_secid_code = cik_secid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_GetCurrentDocId.sql', 'r', encoding='UTF-8') as currentdocid_code:
    currentdocid_code = currentdocid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_GetAllDocId.sql', 'r', encoding='UTF-8') as alldocid_code:
    alldocid_code = alldocid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_Info_CurrentDoc.sql', 'r', encoding='UTF-8') as info_currentdoc_code:
    info_currentdoc_code = info_currentdoc_code.read()


# 由filingid取secid
def get_secid(connection, filingorcik, id):
    cursor = connection.cursor()
    if filingorcik == 1:
        result = cursor.execute(filingid_secid_code % (id)).fetchall()
    else:
        result = cursor.execute(cik_secid_code % (id)).fetchall()
    list_secid = []
    for each in result:
        list_secid.append(each[0])
    cursor.close()
    return list_secid


# 由secid取currentdocid
def get_currentdocid(connection, list_currentdocid, secid, doctype, selecttype, mutex):
    cursor = connection.cursor()
    if selecttype =='currentdocs':
        result = cursor.execute(currentdocid_code %(secid,doctype)).fetchall()
    else:
        result = cursor.execute(alldocid_code %(secid,doctype)).fetchall()
    for each in result:
        list_currentdocid.append(each[0])
    cursor.close()
    return list_currentdocid


# 由docid取currentdoc的信息
def get_info_currentdoc(connection, docid):
    pd_currentdoc = pd.DataFrame()
    result = pd.read_sql(info_currentdoc_code %(docid), connection)
    pd_currentdoc = pd_currentdoc.append(result, ignore_index=True)
    pd_currentdoc = pd_currentdoc.sort_values(by='EffectiveDate', ascending=False)
    return pd_currentdoc


# 线程设置
def getrange(l,r,connection,SecId_list, num, doctype, list_currentdocid, selecttype, mutex):
	for i in range(l,r):
		if i < num:
			secid = SecId_list[i]
			get_currentdocid(connection, list_currentdocid, secid, doctype, selecttype, mutex)


#-----------------------------------------main-------------------------------------------

def run(filingorcik, filingid, doctype, selecttype):
    # 连接数据库
    connection = pyodbc.connect(common.connection_string_multithread)
 
    secid = get_secid(connection, filingorcik, filingid)
    # 设置每个线程的任务量
    totalThread = 20
    num = len(secid)
    gap = math.ceil(float(num) / totalThread)

    list_currentdocid = []
    # 多线程，取currentdoc
    mutex = threading.Lock()
    threadlist = [threading.Thread(target=getrange, args=(i, i+gap, connection, secid, num, doctype, list_currentdocid, selecttype, mutex,)) for i in range(1,num,gap)]
    for t in threadlist:
        t.setDaemon(True)
        t.start()
    for i in threadlist:
        i.join()

    list_currentdocid = list(set(list_currentdocid))
    list_currentdocid = ','.join(map(str,list_currentdocid))
    info_currentdoc = get_info_currentdoc(connection, list_currentdocid)

    html_code ='''
    <!DOCTYPE HTML>
    <html>
      <head>
        <meta charset="utf-8">
        <link rel="shortcut icon" href="/static/img/Favicon.ico" type="image/x-icon"/>
        <title>Map By Doc from CIK</title>
      </head>
    <body>
    <h3>Map By Doc from CIK</h3>
    <table border="1" class="tablestyle">
    <thead>
    <tr style="text-align: right;">
        <th></th>
        <th>DocumentId</th>
        <th>FilingId</th>
        <th>ProcessId</th>
        <th>DocType</th>
        <th>EffectiveDate</th>
        <th>MappingNum</th>
        </tr>
    </thead>
    <tbody>    
    '''
    for row in range(len(info_currentdoc)):
        html_code += '<tr>' + '<td>%s</td>' %row
        for col in range(6):
            if col == 0:
                html_code += '<td><a href=\'http://doc.morningstar.com/document/%s.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b\' target="_blank"> %s </a></td>' % (info_currentdoc.iloc[row,col],info_currentdoc.iloc[row,col])
            else:
                html_code += '<td>%s</td>' % (info_currentdoc.iloc[row,col])
        html_code += '</tr>'
    html_code += '</tbody></table></body></html>'
    html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')
    
    connection.close()