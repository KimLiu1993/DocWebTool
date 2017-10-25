#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/25
#--RevisedDate:
#------------------------------------

import re
import pyodbc
# import pandas as pd
import common


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

with open(common.sql_path + '\\SearchByFundTicker.sql', 'r', encoding='UTF-8') as sql_reader:
    sql_code = sql_reader.read()


def search_doc(regex, content, ignore):
    if ignore == 1:
        reg_key = re.compile(regex, re.IGNORECASE)
    else:
        reg_key = re.compile(regex)
    result = re.findall(reg_key, content)
    result = list(set(result))
    return sorted(result)


def get_secid_byfundname(connection, fundname):
    fundname = str(fundname).lower()
    cursor = connection.cursor()
    cursor.execute(sql_code % (fundname))
    result = cursor.fetchall()
    new_result = []
    if len(result) > 0:
        for row in result:
            row = list(row)
            row.insert(3, '')
            new_result.append(row)
        cursor.close()
        return new_result
    else:
        cursor.close()
        return [[fundname, '', '', '', '', '', '', '']]


def to_html_table(result_list, processid):
    html_code = '<p>ProcessId: ' + processid + '</p><table class=tablestyle >'
    row_num = 0
    for row in result_list:
        if row_num == 0:
            html_code += '<tr>'
            for column in row:
                html_code = html_code + '<th>' + column + '</th>'
            html_code += '</tr>'
        else:
            html_code += '<tr>'
            column_num = 0
            for column in row:
                if column_num == 3:
                    html_code = html_code + '<td><a href="' + common.domain + '/api/v1.0/mapping?processid=' + processid + '&secid=' + secid + '" target="_blank">AddMapping</a></td>'
                else:
                    html_code = html_code + '<td>' + column + '</td>'
                    if column_num == 2:
                        secid = column
                column_num += 1
            html_code += '</tr>'
        row_num += 1
    html_code += '</table>'
    return  html_code


def run(regex, processid, content, ignore):
    connection = pyodbc.connect(common.connection_string_multithread)
    all_fundname = search_doc(regex, content, ignore)

    all_result = []
    for each_fundname in all_fundname:
        secid_list = get_secid_byfundname(connection, each_fundname)
        all_result += secid_list
    # print(all_result)
    # pd_result = pd.DataFrame.from_records(all_result,columns=['FundName','FundId','SecId'])
    # pd.set_option('display.max_colwidth', -1)
    # pd_result.index += 1
    # html_code = pd_result.to_html(classes='tablestyle')
    header = [['FundLegalName', 'FundId', 'SecId', 'AddMapping', 'SecurityName', 'Status', 'Universe', 'CountryId']]
    if all_result is not None:
        all_result = header + all_result
    else:
        all_result = header
    html_code = to_html_table(all_result, processid)
    html_code = css_code + html_code
    connection.close()
    return html_code
