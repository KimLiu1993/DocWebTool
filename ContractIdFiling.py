#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/24
#--RevisedDate:
#------------------------------------

import common
import pyodbc
import pandas as pd

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
    html_code = css_code + html_code
    return html_code
