#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/25
#--RevisedDate:   
#------------------------------------

import common
import pyodbc
import pandas as pd


with open(common.sql_path + '\\MappingTool.sql','r') as MappingTool_code:
    mappingtool_code = MappingTool_code.read()



def get_secid(connection,filingid):
    cursor = connection.cursor()
    result = cursor.execute(mappingtool_code % (filingid)).fetchall()
    
    total_result = []
    for each in result:
        investmenid = each[0]
        doccount = each[1]
        securityname = each[2]
        secidstatus = each[3]
        universe = each[4]
        total = [str(investmenid) + str(doccount) + str(securityname) + str(secidstatus) + str(universe)]
        total_result.append(total)
    cursor.close()
    connection.close()
    return total_result

def run_contractid(filingid):
    total_result = get_secid(connection,filingid)
    pd_result = pd.DataFrame(total_result, columns=['InvestmenId', 'DocCount', 'SecurityName', 'SecidStatus', 'Universe'])
    pd.set_option('display.max_colwidth', -1)
    html_code = pd_result.to_html(classes='tablestyle', index=False)
    html_code = '<p>FilingId: ' + filingid + '</p>' + common.css_code + html_code
    return html_code
    
# filingid = 38601728
# connection = pyodbc.connect(common.connection_string_multithread)
# result = get_secid(connection,filingid)
# print(result)