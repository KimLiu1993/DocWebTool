#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Lychee Li
#--CreationDate:  2017/10/23
#--RevisedDate:
#------------------------------------


import re
import pyodbc
import pandas as pd
import common
import time


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


# 从content中找fund
def serach_fund(regex,content):
    regular = re.compile(regex)
    fund_list = re.findall(regular, content)
    result = list(set(fund_list))
    result.sort(key=fund_list.index)
    return result


def run(regex,content):
    fund_list = serach_fund(regex,content)

    total_result = []
    for each in fund_list:
        items = [each]
        total_result.append(items)
    print(total_result)
    pd_result = pd.DataFrame.from_records(total_result,columns=['FundName/Ticker'])
    pd.set_option('display.max_colwidth', -1)
    pd_result.index += 1
    html_code = pd_result.to_html(classes='tablestyle')
    html_code = css_code + html_code
    return html_code


                




