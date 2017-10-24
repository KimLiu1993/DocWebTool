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


# 读取SQL代码
with open(common.sql_path + '\\MapByDocFromCIK_GetSecId.sql', 'r', encoding='UTF-8') as secid_code:
    secid_code = secid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_GetCurrentDocId.sql', 'r', encoding='UTF-8') as currentdocid_code:
    currentdocid_code = currentdocid_code.read()

with open(common.sql_path + '\\MapByDocFromCIK_Info_CurrentDoc.sql', 'r', encoding='UTF-8') as info_currentdoc_code:
    info_currentdoc_code = info_currentdoc_code.read()


# 由filingid取secid
def get_secid(connection,filingid):
    cursor = connection.cursor()
    result = cursor.execute(secid_code %(filingid)).fetchall()
    list_secid = []
    for each in result:
        list_secid.append(each[0])
    cursor.close()
    return list_secid


# 由secid取currentdocid
def get_currentdocid(connection,secid,doctype):
    for each in secid:
        cursor = connection.cursor()
        result = cursor.execute(currentdocid_code %(each,doctype)).fetchall()
        for each in result:
            list_currentdocid.append(each[0])
        cursor.close()
    list_currentdocid = list(set(list_currentdocid))
    return list_currentdocid


# 由docid取currentdoc的信息
def get_info_currentdoc(connection,docid):
    pd_currentdoc = pd.DataFrame()
    for each in docid:
        result = pd.read_sql(info_currentdoc_code %(each), connection)
        pd_currentdoc = pd_currentdoc.append(result, ignore_index=True)
    pd_currentdoc = pd_currentdoc.sort_values(by='EffectiveDate', ascending=False)
    return pd_currentdoc


# 线程设置
def getrange(l,r,connection,SecId_list,num,doctype, list_currentdocid):
	for i in range(l,r):
		if i < num:
			secid = SecId_list[i]
			get_currentdocid(connection,list_docid,doctype)


#-----------------------------------------main-------------------------------------------

# 连接数据库
connection = pyodbc.connect(common.connection_string_multithread)

filingid = '39559903'
secid = get_secid(connection,filingid)
print(secid)
doctype = 1

# 设置每个线程的任务量
totolthread = 20
num = len(secid)
gap = math.ceil(float(num) / totalThread)

list_currentdocid = []

# 多线程，取currentdoc
mutex = threading.lock()
threadlist = [threading.Thread(target=getrange, args=(i, i+gap, connection, secid, num, list_currentdocid,)) for i in range(1,num,gap)]
for t in threadlist:
    t.setDaemon(True)
    t.start()
for i in threadlist:
    i.join()

info_currentdoc = get_info_currentdoc(connection, list_currentdocid)
print(info_doc)
print(len(info_doc))

html_code = info_currentdoc.to_html(classes='tablestyle', index=False)
