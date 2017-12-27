#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------
#--Author:        Sharol Liu
#--CreationDate:  2017/12/21
#--RevisedDate:   2017/12/21
#------------------------------------


import pyodbc
import common
import pandas as pd


# 读取SQL代码
with open(common.sql_path + '\\MappingTool.sql', 'r', encoding='UTF-8') as mappingtool_code:
    mappingtool_code = mappingtool_code.read()


# 主函数
def run(filingid):
    connection = pyodbc.connect(common.connection_string_multithread)
    result = pd.read_sql(mappingtool_code %(filingid), connection)
    html_table = result.to_html(classes = 'tablestyle', index = False)
    html_code = '<p>FilingId: ' + filingid + '</p>' + common.css_code + html_table
    # html_code = html_code.replace('class="dataframe tablestyle"', 'class="tablestyle"'
    return html_code