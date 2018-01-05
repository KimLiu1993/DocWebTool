#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2018/1/4 8:36
#--RevisedDate:   2018/1/5
#------------------------------------

import time
import sqlite3
import pandas as pd
import common


def get_raw_data(begin_date, end_date, process, resulttype, data_type='Defect'):
    conn = sqlite3.connect(common.Timeliness_DB_path)
    if process == '1':
        if data_type == 'All':
            sql_code = '''
                select * from MFTimeliness as t
                where t.CreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)
        else:
            sql_code = '''
                select * from MFTimeliness as t
                where t.Flag != '<=24BHr' and t.CreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)
    elif process == '2':
        if data_type == 'All':
            sql_code = '''
                select * from VATimeliness as t
                where t.FixedCreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)
        else:
            sql_code = '''
                select * from VATimeliness as t
                where t.Document_Flag != '<=15BHr' and t.FixedCreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)
    else:
        if data_type == 'All':
            sql_code = '''
                select * from UITTimeliness as t
                where t.CreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)
        else:
            sql_code = '''
                select * from UITTimeliness as t
                where t.Flag != '<=24BHr' and t.CreationDateSZ between '%s' and '%s'
            ''' % (begin_date, end_date)

    Raw_data_detail_list = pd.read_sql(sql_code, conn)
    Raw_data_detail_list.index += 1

    if resulttype == 'HTML':
        html_code = Raw_data_detail_list.to_html(classes='bordered')
        html_code = common.css_code_Timeliness + html_code
        conn.close()
        return html_code
    else:
        result_file = 'Reslut-' + time.strftime('%Y%m%d') + time.strftime('%H%M%S') + '.csv'
        try:
            Raw_data_detail_list.to_csv(common.temp_path + result_file, encoding='UTF-8')
        except:
            Raw_data_detail_list.to_csv(common.temp_path + result_file, encoding='GB18030')
        conn.close()
        return result_file


def get_Pivot_Table(begin_date, end_date, process):
    conn = sqlite3.connect(common.Timeliness_DB_path)
    if process == '1':
        sql_code = '''
            select * from MFTimeliness as t
            where t.CreationDateSZ between '%s' and '%s'
        ''' % (begin_date, end_date)

        detail_list = pd.read_sql(sql_code, conn)
        detail_list['Date'] = pd.to_datetime(detail_list['FixedCreationDateSZ'], errors='coerce').dt.strftime('%Y-%m')

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_bar = pivot_table
        pivot_table_bar.columns = pivot_table_bar.columns.droplevel(0)
        pivot_table_bar.columns.name = None
        pivot_table_bar = pivot_table_bar.rename_axis(None, axis=1)

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_percentage = pivot_table.div(pivot_table.iloc[:,-1],axis=0)
        pivot_table_percentage = pivot_table_percentage.loc[:,pivot_table_percentage.columns.get_level_values(1).isin(['<=24BHr', '>24BHr'])]
        pivot_table_percentage = pivot_table_percentage[pivot_table_percentage.index != 'All']
        pivot_table_percentage_new = pivot_table_percentage
        pivot_table_percentage_new.columns = pivot_table_percentage.columns.droplevel(0)
        pivot_table_percentage_new.columns.name = None
        pivot_table_percentage_new = pivot_table_percentage_new.rename_axis(None, axis=1)

    elif process == '2':
        sql_code = '''
            select * from VATimeliness as t
            where t.FixedCreationDateSZ between '%s' and '%s'
        ''' % (begin_date, end_date)

        detail_list = pd.read_sql(sql_code, conn)
        detail_list['Date'] = pd.to_datetime(detail_list['FixedCreationDateSZ'], errors='coerce').dt.strftime('%Y-%m')

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Time_Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_bar = pivot_table
        pivot_table_bar.columns = pivot_table_bar.columns.droplevel(0)
        pivot_table_bar.columns.name = None
        pivot_table_bar = pivot_table_bar.rename_axis(None, axis=1)

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Time_Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_percentage = pivot_table.div(pivot_table.iloc[:, -1], axis=0)
        pivot_table_percentage = pivot_table_percentage.loc[:, pivot_table_percentage.columns.get_level_values(1).isin(['<=15BHr', '>15BHr'])]
        pivot_table_percentage = pivot_table_percentage[pivot_table_percentage.index != 'All']
        pivot_table_percentage_new = pivot_table_percentage
        pivot_table_percentage_new.columns = pivot_table_percentage.columns.droplevel(0)
        pivot_table_percentage_new.columns.name = None
        pivot_table_percentage_new = pivot_table_percentage_new.rename_axis(None, axis=1)

    else:
        sql_code = '''
            select * from UITTimeliness as t
            where t.FixedCreationDateSZ between '%s' and '%s'
        ''' % (begin_date, end_date)

        detail_list = pd.read_sql(sql_code, conn)
        detail_list['Date'] = pd.to_datetime(detail_list['FixedCreationDateSZ'], errors='coerce').dt.strftime('%Y-%m')

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Document_Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_bar = pivot_table
        pivot_table_bar.columns = pivot_table_bar.columns.droplevel(0)
        pivot_table_bar.columns.name = None
        pivot_table_bar = pivot_table_bar.rename_axis(None, axis=1)

        pivot_table = pd.pivot_table(detail_list, index=['Date'], columns=['Document_Flag'], values=['ProcessId'], aggfunc=len, fill_value=0, margins=True)
        pivot_table_percentage = pivot_table.div(pivot_table.iloc[:, -1], axis=0)
        pivot_table_percentage = pivot_table_percentage.loc[:, pivot_table_percentage.columns.get_level_values(1).isin(['<=15BHr', '>15BHr'])]
        pivot_table_percentage = pivot_table_percentage[pivot_table_percentage.index != 'All']
        pivot_table_percentage_new = pivot_table_percentage
        pivot_table_percentage_new.columns = pivot_table_percentage.columns.droplevel(0)
        pivot_table_percentage_new.columns.name = None
        pivot_table_percentage_new = pivot_table_percentage_new.rename_axis(None, axis=1)

    blank_str = '''
        <br/><br/>
        <br/><br/>
        <br/><br/>
    '''
    html_code_1 = pivot_table_bar.to_html(classes='bordered')
    html_code_2 = pivot_table_percentage_new.to_html(classes='bordered', formatters={'<=24BHr': '{:,.2%}'.format, '>24BHr': '{:,.2%}'.format})

    html_code = common.css_code_Timeliness + html_code_2 + blank_str + html_code_1

    return html_code