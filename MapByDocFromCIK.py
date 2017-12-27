#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Sharol Liu
#--CreationDate:  2017/10/23
#--RevisedDate:   2017/10/31
#------------------------------------

import common
import pyodbc
import pandas as pd
import math
import threading

# 读取SQL代码
with open(common.sql_path + '\\MapByDocFromCIK_IsDuplicate.sql', 'r', encoding='UTF-8') as isduplicate_code:
    isduplicate_code = isduplicate_code.read()
    
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
    if filingorcik == '1':
        filingid = isduplicate(connection,id)
        result = cursor.execute(filingid_secid_code % (filingid)).fetchall()
    else:
        result = cursor.execute(cik_secid_code % (id)).fetchall()
    list_secid = []
    if len(result)>0:
        for each in result:
            list_secid.append(each[0])
    cursor.close()
    return list_secid


# 找全duplicate filing的filingid
def isduplicate(connection, id):
    cursor = connection.cursor()
    result = cursor.execute(isduplicate_code % (id)).fetchall()
    if len(result)>0:
        r = result[0][0]
        if r[-2] ==',':
            r = r[r.find('[')+1:r.find(']')-1]
            return r + ',' + str(id)
        else:
            r = r[r.find('[')+1:r.find(']')]
            return r + ',' + str(id)
    else:
        return id


# 由secid取currentdocid
def get_currentdocid(connection, list_currentdocid, secid, doctype, selecttype, mutex):
    cursor = connection.cursor()
    if selecttype =='currentdocs':
        result = cursor.execute(currentdocid_code %(secid,doctype)).fetchall()
    else:
        result = cursor.execute(alldocid_code %(secid,doctype)).fetchall()
    if len(result)>0:
        for each in result:
            list_currentdocid.append(each[0])
    cursor.close()
    return list_currentdocid


# 由docid取currentdoc的信息
def get_info_currentdoc(connection, docid):
    cursor = connection.cursor()
    pd_currentdoc = pd.DataFrame()
    result = pd.read_sql(info_currentdoc_code %(docid), connection)
    pd_currentdoc = pd_currentdoc.append(result, ignore_index=True)
    cursor.close()
    return pd_currentdoc


# 线程设置
def getrange(l,r,connection,SecId_list, num, doctype, list_currentdocid, selecttype, mutex):
    for i in range(l,r):
        if i < num:
            secid = SecId_list[i]
            get_currentdocid(connection, list_currentdocid, secid, doctype, selecttype, mutex)


def run(filingorcik, filingid, doctype, selecttype):
    try:
        # 连接数据库
        connection = pyodbc.connect(common.connection_string_multithread)

        secid = get_secid(connection, filingorcik, filingid)
        if len(secid) < 1 :
            list_currentdocid = []
        else:
            # 设置每个线程的任务量
            totalThread = 30
            num = len(secid)
            if num < 30:
                totalThread = num
            gap = math.ceil(float(num) / totalThread)

            list_currentdocid = []
            # 多线程，取currentdoc
            mutex = threading.Lock()
            threadlist = [threading.Thread(target=getrange, args=(i, i+gap, connection, secid, num, doctype, list_currentdocid, selecttype, mutex,)) for i in range(0,num,gap)]
            for t in threadlist:
                t.setDaemon(True)
                t.start()
            for i in threadlist:
                i.join()
        
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
            '''
        if filingorcik == '1':
            html_code += 'FilingId = ' + filingid +'<br/><br/>'
        else:
            html_code += 'CIK = ' + filingid
        html_table = '''
            <table border="1" class="tablestyle">
            <thead>
            <tr style="text-align: right;">
                <th>No.</th>
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
        html_code += html_table
        
        if len(list_currentdocid) < 1:
            html_code += '</tbody></table></body></html>'
            html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')
        else:  
            list_currentdocid = list(set(list_currentdocid))
            list_currentdocid = ','.join(map(str,list_currentdocid))
            info_currentdoc = get_info_currentdoc(connection, list_currentdocid)

            for row in range(len(info_currentdoc)):
                html_code += '<tr>' + '<td>%s</td>' %str(row + 1)
                for col in range(6):
                    if col == 0:
                        html_code += '<td><a href="http://doc.morningstar.com/document/%s.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b" target="_blank"> %s </a></td>' % (info_currentdoc.iloc[row,col],info_currentdoc.iloc[row,col])
                    else:
                        html_code += '<td>%s</td>' % (info_currentdoc.iloc[row,col])
                html_code += '</tr>'
            html_code += '</tbody></table></body></html>'
            html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')

        connection.close()
        return html_code
    except Exception as e:
        return str(e)
    


