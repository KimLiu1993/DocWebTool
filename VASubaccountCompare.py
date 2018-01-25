#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2018/1/25 9:54
#--RevisedDate:   
#------------------------------------

import difflib
import datetime
import pyodbc
import pandas as pd
import common


def get_doc_mapping(connection, docid):
    cursor = connection.cursor()
    code = '''
        select distinct im.InvestmentId from DocumentAcquisition..InvestmentMapping im
        left join DocumentAcquisition..MasterProcess mp on mp.ProcessId=im.ProcessId
        where mp.DocumentId=%s
    ''' % (docid)
    result = cursor.execute(code).fetchall()
    policy_id_list = [row[0] for row in result]
    cursor.close()
    return policy_id_list


def get_subaccount_info(connection, policyid):
    cursor = connection.cursor()
    code = '''
        select A.SubaccountId,A.LegalName,A.CloseToNewInvestorsDate,A.PolicyId
        from [TimeSeries].[dbo].[Subaccount] as A
        where A.Status=1 and A.PolicyId='%s'
    ''' % (policyid)
    result = cursor.execute(code).fetchall()
    cursor.close()
    return result


def compare(legalname, fundname):
    ratio = difflib.SequenceMatcher(None, legalname, fundname).ratio()
    return ratio


def run(docid, fund_content_name_list_string):

    fund_content_name_list = []
    fn1 = fund_content_name_list_string.split('\n')
    for line in fn1:
        if len(line) > 0:
            line = line.strip()
            line = line.rstrip('\r')
            fund_content_name_list.append(line)

    connection_string = 'Driver={SQL Server Native Client 11.0};Server=dcdrdb601\dminputdb;Database=DocumentAcquisition;Uid=xxx;Pwd=xxx;Trusted_Domain=msdomain1;Trusted_Connection=yes;MARS_Connection=yes;'
    connection = pyodbc.connect(connection_string)

    policy_id_list = get_doc_mapping(connection, docid)

    total_result = []

    policy_subaccount_dict = {}
    for policyid in policy_id_list:
        policy_subaccount_dict[policyid] = get_subaccount_info(connection, policyid)

    for fundname in fund_content_name_list:
        for policyid in policy_id_list:
            subaccount_info = policy_subaccount_dict[policyid]
            ratio_list = [compare(key[1], fundname) for key in subaccount_info]
            ratio = max(ratio_list)
            max_ratio_index = ratio_list.index(ratio)
            subaccount_list = subaccount_info[max_ratio_index]
            subaccountid = subaccount_list[0]
            legalname = subaccount_list[1]

            closedate = subaccount_list[2]
            result = (fundname, policyid, subaccountid, legalname, closedate, '{0:.2f}%'.format(ratio * 100))
            print(result)
            total_result.append(result)

    pd_result = pd.DataFrame.from_records(total_result, columns = ['FundName', 'PolicyId', 'SubaccountId', 'LegalName', 'CloseDate', 'Similarity'])
    excel_name = 'VASubaccountCompareResult-' + datetime.datetime.now().strftime('%Y%m%d') + '.xlsx'
    pd_result.to_excel(common.temp_path + excel_name, encoding='UTF-8', index=False)

    connection.close()

    return excel_name