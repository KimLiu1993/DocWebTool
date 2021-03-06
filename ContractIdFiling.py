#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/24
#--RevisedDate:   2017/10/25
#------------------------------------

import common
import pyodbc
import pandas as pd

with open(common.sql_path + '\\ContractId_Filing.sql', 'r', encoding='UTF-8') as contractid_filing_code:
    contractid_filing = contractid_filing_code.read()


# 从contractid中得到filing的相关信息
def get_filing(contractid):
    connection = pyodbc.connect(common.connection_string_multithread)
    cursor = connection.cursor()
    result = cursor.execute(contractid_filing % (contractid)).fetchall()

    all_result = []
    for each in result:
        Contractid = each[0]
        Seriesname = each[1]
        Contractname = each[2]
        Cik = each[3]
        Filingid = each[4]
        Accession = each[5]
        Formtype = each[6]
        Filedate = each[7]
        total_result = [Contractid, Seriesname, Contractname, Cik, Filingid, Accession, Formtype, Filedate.strftime('%Y-%m-%d %H:%M:%S')]
        # print(total_result)
        all_result.append(total_result)
    cursor.close()
    connection.close()
    return all_result


def run_contractid(contractid):
    total_result = get_filing(contractid)
    pd_result = pd.DataFrame(total_result, columns=['ContractId', 'SeriesName', 'ContractName', 'Cik', 'FilingId', 'Accession', 'Formtype', 'Filedate'])
    pd.set_option('display.max_colwidth', -1)
    html_code = pd_result.to_html(classes='tablestyle', index=False)
    html_code = common.css_code + html_code
    return html_code
