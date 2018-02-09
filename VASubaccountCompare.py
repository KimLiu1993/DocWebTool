#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2018/1/25 9:54
#--RevisedDate:   2018/2/7
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
        select A.SubaccountId,B.SecurityName,A.CloseToNewInvestorsDate,A.PolicyId
        from [CurrentData].[dbo].[Subaccount] as A
        Left join [SecurityData].[dbo].[SecuritySearch] as B on A.FundShareClassId=B.SecId
        where A.Status=1 and A.PolicyId='%s'
        ''' % (policyid)
    result = cursor.execute(code).fetchall()
    subaccount_info = {}
    null_list = []
    
    for i in result:
        if i[1] is not None:
            subaccount_info[i[1]] = (i[0], i[2])
            null_list = []
        elif i[2] is not None:
            closedate = i[2].strftime('%Y-%m-%d %H:%M:%S')
            i_list = ['', policyid, i[0], i[1], closedate, '']
            null_list.append(i_list)
        else:
            i_list = ['', policyid, i[0], i[1], '', '']
            null_list.append(i_list)
    return null_list, subaccount_info


def compare(fundname, securityname):
    ratio = difflib.SequenceMatcher(None, fundname, securityname).ratio()
    return ratio


def run(docid, fundname_string):

    fund_name_list = []
    if '\n' in fundname_string:
        fund = fundname_string.split('\n')
        for line in fund:
            if len(line) > 0:
                line = line.strip()
                line = line.rstrip('\r')
                fund_name_list.append(line)
    else:
        fund_name_list.append(fundname_string)

    connection = pyodbc.connect(common.connection_string_multithread)

    policy_id_list = get_doc_mapping(connection, docid)

    total_result = []

    for policyid in policy_id_list:
        policyid_result = []
        subaccount_result = get_subaccount_info(connection, policyid)
        null_list = subaccount_result[0]
        temp_null_result = null_list[:]

        subaccount_info = subaccount_result[1]
        securityname_list = subaccount_info.keys()

        ratio_list = [(fundname, securityname, compare(fundname, securityname)) for fundname in fund_name_list for securityname in securityname_list]
        pd_result = pd.DataFrame(ratio_list, columns=['FundName', 'SecurityName', 'Ratio']).sort_values(by='Ratio', ascending=False)

        while pd_result.shape[0]>0:
            temp_target = tuple(pd_result.head(1).values.tolist()[0])
            temp_fundname = temp_target[0]
            temp_security_name = temp_target[1]
            ratio = temp_target[2]
            subaccountid = subaccount_info[temp_security_name][0]
            
            closedate = subaccount_info[temp_security_name][1]

            if closedate is not None:
                closedate = closedate.strftime('%Y-%m-%d %H:%M:%S')
            else:
                closedate = ''
            
            result = (temp_fundname, policyid, subaccountid, temp_security_name, closedate, '{0:.2f}%'.format(ratio * 100))
            policyid_result.append(result)
            

            if pd_result.shape[0]>0:
                pd_result = pd_result[pd_result['FundName'] != temp_fundname]
            if pd_result.shape[0]>0:
                pd_result = pd_result[pd_result['SecurityName'] != temp_security_name]
                
        temp_total_result = policyid_result[:]

        if len(fund_name_list) >= len(subaccount_info):
            temp_list = [i for i in fund_name_list if i not in [items[0] for items in policyid_result]]
            temp_result = [(i, policyid, '', '', '', '0') for i in temp_list]
            total_result = total_result + temp_total_result + temp_result + temp_null_result
        else:
            temp_list = [i for i in securityname_list if i not in [items[3] for items in policyid_result]]
            temp_result = []
            for each in temp_list:
                temp_subaccountid = subaccount_info[each][0]
                temp_closedate = subaccount_info[each][1]

                if temp_closedate is not None:
                    temp_closedate = temp_closedate.strftime('%Y-%m-%d %H:%M:%S')
                
                temp = ('', policyid, temp_subaccountid, each, temp_closedate, '0')
                temp_result.append(temp)
            total_result = total_result + temp_total_result + temp_result + temp_null_result

    pd_total_result = pd.DataFrame.from_records(total_result, columns=['FundName', 'PolicyId', 'SubaccountId', 'SecName', 'CloseDate', 'Similarity'])
    excel_name = 'VASubaccountCompareResult-' + str(docid) + '-' + datetime.datetime.now().strftime('%Y%m%d') + '.xlsx'
    pd_total_result.to_excel(common.temp_path + excel_name, encoding='UTF-8', index=False)
    connection.close()

    return excel_name
    

# docid = 132735313
# fundname_string = 'ALPS Variable Investment Trust - ALPS/Alerian Energy Infrastructure Portfolio: Class III\nALPS Variable Investment Trust - ALPS/Red Rocks Listed Private Equity Portfolio: Class III'
# a = run(docid, fundname_string)
# print(a)




    # connection.close()

    # return excel_name
    # policy_subaccount_dict = {}
    # for policyid in policy_id_list:
    #     policy_subaccount_dict[policyid] = get_subaccount_info(connection, policyid)

    # for fundname in fund_content_name_list:
    #     for policyid in policy_id_list:
    #         subaccount_info = policy_subaccount_dict[policyid]
    #         ratio_list = []

    #         for key in subaccount_info:
    #             print(key)
    #             print(fundname)
    #             print('')
    #             ratio = compare(key[1], fundname)
    #             ratio_list.append(ratio)

    #         # ratio_list = [compare(key[1], fundname) for key in subaccount_info]
    #         ratio = max(ratio_list)
    #         max_ratio_index = ratio_list.index(ratio)
    #         subaccount_list = subaccount_info[max_ratio_index]
    #         subaccountid = subaccount_list[0]
    #         legalname = subaccount_list[1]

    #         closedate = subaccount_list[2]
    #         result = (fundname, policyid, subaccountid, legalname, closedate, '{0:.2f}%'.format(ratio * 100))
    #         print(result)
    #         total_result.append(result)

    # pd_result = pd.DataFrame.from_records(total_result, columns = ['FundName', 'PolicyId', 'SubaccountId', 'SecName', 'CloseDate', 'Similarity'])
    # excel_name = 'VASubaccountCompareResult-' + datetime.datetime.now().strftime('%Y%m%d') + '.xlsx'
    # pd_result.to_excel(common.temp_path + excel_name, encoding='UTF-8', index=False)

    # connection.close()

    # return excel_name