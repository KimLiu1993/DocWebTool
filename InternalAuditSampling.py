#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/12/18 17:51
#--RevisedDate:   2018/01/15
#------------------------------------

import datetime
import random
import pyodbc
import pandas as pd
import common


def convert_id(x):
    x = str(x)
    id_list = []
    ids1 = x.split('\n')
    for line in ids1:
        line = line.strip('\n')
        line = line.strip('\r')
        id_list.append(line)
    return id_list


def run(month_diff, Last_Checked_SecId):

    try:

        print('Starting...\n')

        last_check_secid_list = convert_id(Last_Checked_SecId)

        connection_string = 'Driver={SQL Server};Server=dcdrdb601\dminputdb;Database=DocumentAcquisition;Uid=xxx;Pwd=xxx;Trusted_Domain=msdomain1;Trusted_Connection=yes;MARS_Connection=yes;'
        connection = pyodbc.connect(connection_string)

        current_month = datetime.datetime.now().month

        # if current_month <= 6:
        #     # 1-6月，则取前一个月的SecId作为Pool
        #     month_diff = 1
        # else:
        #     # 7-12月，则取前两个月的SecId作为Pool
        #     month_diff = 2
        # print(
        #     'The month is %d, it is sampling the SecIds from %d month before...\n'
        #     % (current_month, month_diff))

        # month_diff = 1
        # month_diff = int(input('Please input you want to sample the SecIds how many months before, then press Enter：'))

        sql_code_secid_pool = '''
            select distinct ss.SecId,count(distinct mp.ProcessId) as [DocNum]
            from SecurityData..SecuritySearch ss
            left join DocumentAcquisition..SECCurrentDocument cd on cd.InvestmentId=ss.SecId
            left join DocumentAcquisition..MasterProcess mp on mp.DocumentId=cd.DocumentId
            where cd.UpdateDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and cd.UpdateDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.Universe in (
                        '/OEIC/',
                        '/OEIC/529/',
                        '/OEIC/ETF/',
                        '/OEIC/ETMF/',
                        '/OEIC/HF/',
                        '/OEIC/Ins/',
                        '/OEIC/Ins/Pen/',
                        '/OEIC/Ins/Ret/',
                        '/OEIC/MM/',
                        '/OEIC/MM/Ins/',
                        '/OEIC/MM/Ins/Pen/',
                        '/OEIC/MM/Ins/Ret/',
                        '/OEIC/MM/Pen/',
                        '/OEIC/MM/Ret/',
                        '/OEIC/Pen/',
                        '/OEIC/Ret/',
                        '/CEIC/',
                        '/CEIC/ETF/',
                        '/CEIC/HF/'
                    )
                    and ss.Status=1
                    and ss.CountryId='USA'
                    and mp.Status=10
                    and mp.Category=1
                    and mp.Format!='PDF'
                    and mp.CreationDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and mp.CreationDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
            group by ss.SecId
            order by count(distinct mp.ProcessId) desc
        '''
        cursor = connection.cursor()
        target_all_secid_list = [
            row[0]
            for row in cursor.execute(sql_code_secid_pool % (
                month_diff, month_diff, month_diff, month_diff)).fetchall()
            ]
        cursor.close()

        # 获取上次Check过的SecId
        # if os.path.isfile(cur_file_dir() + '\\Last_Checked_SecId.txt'):
        #     with open(
        #                     cur_file_dir() + '\\Last_Checked_SecId.txt',
        #             'r',
        #             encoding='UTF-8') as r:
        #         last_check_secid_list = list(
        #             set([
        #                     each
        #                     for each in [
        #                         line.strip('\n') for line in r.readlines()
        #                         ] if len(each)
        #                     ]))
        # else:
        #     error = input(
        #         'Cannot find the "Last_Checked_SecId.txt", please add this file, press any button to exit...'
        #     )
        #     sys.exit()

        # 在本次样本池中去掉上次Check过的SecId
        target_all_secid_no_last_check = [
            secid for secid in target_all_secid_list
            if secid not in last_check_secid_list
            ]

        # 从样本池中取Map过Pros、SAI、SP、Supplement类总数最多的50个SecId
        target_secid_list_string = str(target_all_secid_no_last_check).replace('[', '').replace(']', '')
        sql_code_pros_sai_sp = '''
            select distinct top 50 ss.SecId,count(distinct mp.ProcessId) as [DocNum]
            from SecurityData..SecuritySearch ss
            left join DocumentAcquisition..SECCurrentDocument cd on cd.InvestmentId=ss.SecId
            left join DocumentAcquisition..MasterProcess mp on mp.DocumentId=cd.DocumentId
            where cd.UpdateDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and cd.UpdateDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.Universe in (
                        '/OEIC/',
                        '/OEIC/529/',
                        '/OEIC/ETF/',
                        '/OEIC/ETMF/',
                        '/OEIC/HF/',
                        '/OEIC/Ins/',
                        '/OEIC/Ins/Pen/',
                        '/OEIC/Ins/Ret/',
                        '/OEIC/MM/',
                        '/OEIC/MM/Ins/',
                        '/OEIC/MM/Ins/Pen/',
                        '/OEIC/MM/Ins/Ret/',
                        '/OEIC/MM/Pen/',
                        '/OEIC/MM/Ret/',
                        '/OEIC/Pen/',
                        '/OEIC/Ret/',
                        '/CEIC/',
                        '/CEIC/ETF/',
                        '/CEIC/HF/'
                    )
                    and ss.Status=1
                    and ss.CountryId='USA'
                    and mp.Status=10
                    and mp.Category=1
                    and mp.Format!='PDF'
                    and mp.DocumentType in (1,2,3,15,17,60)
                    and mp.CreationDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and mp.CreationDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.SecId in (%s)
            group by ss.SecId
            order by count(distinct mp.ProcessId) desc
        '''
        cursor = connection.cursor()
        pros_secid_list_50 = [
            row[0]
            for row in cursor.execute(sql_code_pros_sai_sp % (
                month_diff, month_diff, month_diff, month_diff, target_secid_list_string)).fetchall()
            ]

        # 50个SecId中随机抽20个
        pros_secid_list = random.sample(pros_secid_list_50, 20)

        target_all_secid_no_last_check_1 = [
            secid for secid in target_all_secid_no_last_check
            if secid not in pros_secid_list
            ]

        # 从样本池中取Map过AR总数最多的50个SecId
        if len(pros_secid_list) < 20:
            ar_num = (20 - len(pros_secid_list)) + 50
        else:
            ar_num = 50
        target_secid_list_string = str(target_all_secid_no_last_check_1).replace('[', '').replace(']', '')
        sql_code_ar_sar = '''
            select distinct top %d ss.SecId,count(distinct mp.ProcessId) as [DocNum]
            from SecurityData..SecuritySearch ss
            left join DocumentAcquisition..SECCurrentDocument cd on cd.InvestmentId=ss.SecId
            left join DocumentAcquisition..MasterProcess mp on mp.DocumentId=cd.DocumentId
            where cd.UpdateDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and cd.UpdateDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.Universe in (
                        '/OEIC/',
                        '/OEIC/529/',
                        '/OEIC/ETF/',
                        '/OEIC/ETMF/',
                        '/OEIC/HF/',
                        '/OEIC/Ins/',
                        '/OEIC/Ins/Pen/',
                        '/OEIC/Ins/Ret/',
                        '/OEIC/MM/',
                        '/OEIC/MM/Ins/',
                        '/OEIC/MM/Ins/Pen/',
                        '/OEIC/MM/Ins/Ret/',
                        '/OEIC/MM/Pen/',
                        '/OEIC/MM/Ret/',
                        '/OEIC/Pen/',
                        '/OEIC/Ret/',
                        '/CEIC/',
                        '/CEIC/ETF/',
                        '/CEIC/HF/'
                    )
                    and ss.Status=1
                    and ss.CountryId='USA'
                    and mp.Status=10
                    and mp.Category=1
                    and mp.Format!='PDF'
                    and mp.DocumentType=4
                    and mp.CreationDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and mp.CreationDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.SecId in (%s)
            group by ss.SecId
            order by count(distinct mp.ProcessId) desc
        '''
        cursor = connection.cursor()
        AR_secid_list_50 = [
            row[0]
            for row in cursor.execute(sql_code_ar_sar % (
                ar_num, month_diff, month_diff, month_diff, month_diff, target_secid_list_string)).fetchall()
            ]

        # 50个SecId中随机抽20个
        AR_secid_list = random.sample(AR_secid_list_50, 20)

        target_all_secid_no_last_check_2 = [
            secid for secid in target_all_secid_no_last_check_1
            if secid not in AR_secid_list
            ]

        # 从样本池中取Map过SAR总数最多的50个SecId
        if len(AR_secid_list) + len(pros_secid_list) < 40:
            sup_num = (40 - (len(AR_secid_list) + len(pros_secid_list))) + 50
        else:
            sup_num = 50
        target_secid_list_string = str(target_all_secid_no_last_check_2).replace('[', '').replace(']', '')
        sql_code_sup = '''
            select distinct top %d ss.SecId,count(distinct mp.ProcessId) as [DocNum]
            from SecurityData..SecuritySearch ss
            left join DocumentAcquisition..SECCurrentDocument cd on cd.InvestmentId=ss.SecId
            left join DocumentAcquisition..MasterProcess mp on mp.DocumentId=cd.DocumentId
            where cd.UpdateDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and cd.UpdateDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.Universe in (
                        '/OEIC/',
                        '/OEIC/529/',
                        '/OEIC/ETF/',
                        '/OEIC/ETMF/',
                        '/OEIC/HF/',
                        '/OEIC/Ins/',
                        '/OEIC/Ins/Pen/',
                        '/OEIC/Ins/Ret/',
                        '/OEIC/MM/',
                        '/OEIC/MM/Ins/',
                        '/OEIC/MM/Ins/Pen/',
                        '/OEIC/MM/Ins/Ret/',
                        '/OEIC/MM/Pen/',
                        '/OEIC/MM/Ret/',
                        '/OEIC/Pen/',
                        '/OEIC/Ret/',
                        '/CEIC/',
                        '/CEIC/ETF/',
                        '/CEIC/HF/'
                    )
                    and ss.Status=1
                    and ss.CountryId='USA'
                    and mp.Status=10
                    and mp.Category=1
                    and mp.Format!='PDF'
                    and mp.DocumentType=5
                    and mp.CreationDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    and mp.CreationDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    and ss.SecId in (%s)
            group by ss.SecId
            order by count(distinct mp.ProcessId) desc
        '''
        cursor = connection.cursor()
        SAR_secid_list_50 = [
            row[0]
            for row in cursor.execute(sql_code_sup % (
                sup_num, month_diff, month_diff, month_diff, month_diff, target_secid_list_string)).fetchall()
            ]

        # 50个SecId中随机抽20个
        SAR_secid_list = random.sample(SAR_secid_list_50, 20)

        target_secid_list = pros_secid_list + AR_secid_list + SAR_secid_list
        target_secid_list_string = str(target_secid_list).replace('[', '').replace(']', '')

        # # 取Map Doc数量最多的40个SecId
        # part1_secid_list = [
        #     secid for secid in target_all_secid_no_last_check[0:40]
        # ]
        # # 剩下的SecId中随机取20个
        # part2_secid_list = random.sample(
        #     [secid for secid in target_all_secid_no_last_check[40:]], 20)

        # print('Sampling the documents, please waiting...\n')

        # target_secid_list = part1_secid_list + part2_secid_list
        # target_secid_list_string = str(target_secid_list).replace('[','').replace(']', '')

        # 抽取60个SecId的Current Doc
        sql_code_get_doc = '''
            select ss.SecId,ss.SecurityName,cim.ContractId,ss.Ticker,cs.CIK,ss.FundId,ss.Universe,
                    sp.Value as [DocType],CONVERT(varchar(10),mp.EffectiveDate,120) as [EffectiveDate],mp.DocumentId,
                    mp.CreationDate,CONVERT(varchar(10),mp.DocumentDate,120) as [DocumentDate],mp.Format,
                    [Checker]='',
                    [Free or Defect]='',
                    [Comment]='',
                    [Confirm DA]='',
                    [DA Confirmation]='',
                    [Confirmation Comment]=''
            from SecurityData..SecuritySearch as ss
            left join DocumentAcquisition..ContractIdInvestmentMapping as cim on cim.InvestmentId=ss.SecId
            left join SecurityData..FundSearch as fs on fs.FundId=ss.FundId
            left join SecurityData..CompanySearch as cs on cs.CompanyId=fs.RegistrantId
            left join DocumentAcquisition..SECCurrentDocument as cdi on cdi.InvestmentId=ss.SecId
            left join DocumentAcquisition..MasterProcess as mp on cdi.DocumentId=mp.DocumentId
            left join DocumentAcquisition..SystemParameter as sp on sp.CodeInt=mp.DocumentType and sp.CategoryId=105
            where --mp.CreationDate>=cast(convert(char(10),dateadd(dd,-day(dateadd(month,-%d,getdate()))+1,dateadd(month,-%d,getdate())),120) as datetime)
                    --and mp.CreationDate<cast(convert(char(10),dateadd(dd,-day(getdate())+1,getdate()),120) as datetime)
                    --and
                    ss.SecId in (%s) and mp.Format='HTM'
                    and mp.DocumentType in (1,2,3,4,5,15,17,60,62)
            order by CONVERT(varchar(10),mp.DocumentDate,120) desc
        '''
        pd_doc_list = pd.read_sql(sql_code_get_doc %
                                  (month_diff, month_diff,
                                   target_secid_list_string), connection)

        print('Saving the result Excel file...\n')
        excel_file = 'Audit Sample-' + datetime.datetime.now().strftime('%Y%m%d') + '.xlsx'
        pd_doc_list.to_excel(common.temp_path + excel_file,
            index=False,
            encoding='UTF-8')
        connection.close()

        print('All done! It will be closed in 10 seconds.')

        return excel_file
    except Exception as e:
        print(str(e))
        return str(e)

