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
    list_result = []
    for each in result:
        list_result.append(each[0])
    cursor.close()
    return list_result


# 由secid取currentdocid
def get_currentdocid(connection,secid,doctype):
    list_result = []
    for each in secid:
        cursor = connection.cursor()
        result = cursor.execute(currentdocid_code %(each,doctype)).fetchall()
        for each in result:
            list_result.append(each[0])
        cursor.close()
    list_result = list(set(list_result))
    return list_result


# 由docid取currentdoc的信息
def get_info_currentdoc(connection,docid):
    pd_result = pd.DataFrame()
    for each in docid:
        result = pd.read_sql(info_currentdoc_code %(each), connection)
        pd_result = pd_result.append(result, ignore_index=True)
    pd_result = pd_result.sort_values(by='EffectiveDate', ascending=False)
    return pd_result

# 连接数据库
connection = pyodbc.connect(common.connection_string_multithread)


filingid = '39559903'
secid = get_secid(connection,filingid)
print(secid)
doctype = 1
docid = get_currentdocid(connection,secid,doctype)
print(docid)
info_doc = get_info_currentdoc(connection,docid)
print(info_doc)
print(len(info_doc))
