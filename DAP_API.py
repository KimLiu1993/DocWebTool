#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# ------------------------------------
# --Author:        Jeffrey Yu
# --CreationDate:  2017/08/04
# --RevisedDate:   2017/10/17
# ------------------------------------

import requests
import json
import datetime
import time


# {'ciks': None, 'docModel': None, 'documentAPIService': {'timeOut': 1800000}, 'exist': False, 'existsNoCDocSecId': None, 'form': {'categoryId': None, 'cik': None, 'companyName': None, 'companyOwner': None, 'contractIds': None, 'contractName': None, 'creationDateFrom': None, 'creationDateTo': None, 'currentProcessId': 44786843, 'docList': None, 'documentIds': None, 'documentType': None, 'existedDoc': None, 'filingIds': None, 'firstOpen': None, 'formType': None, 'investmentIds': None, 'isCurrentDoc': None, 'mappingRule': None, 'newInvstmentLst': None, 'owner': None, 'processIds': None, 'qcRuleId': None, 'status': None, 'updateUserId': 1224}, 'investModel': None, 'investmentProcessModel': None, 'metaData': None, 'metaDocData': None, 'model': None, 'page': None, 'secDocumentRootPath': '/data/app/mount/edgar/doc', 'timeLogModel': None}
def runQC(userid, processid):
    url = 'http://dcweb613/GED/Sec/runSECQc.action'
    data = {"form.currentProcessId": processid, "form.updateUserId": userid}
    req = requests.get(url, timeout=300, params=data)
    return req.json()


# [{"dictionaryId":null,"order":0,"page":"1","rows":[{"check":true,"fundId":"FSUSA001T7","investmentId":"F000005GSN","investmentName":"Salient International Small Cap Advisor","investmentType":1,"legalName":"Salient International Small Cap Fund Class Advisor","matchRatio":100,"parentValue":"F000005GSN","providerId":"0C00009CAB","providerName":"Salient Funds","status":0,"total":1,"umbrellaId":null,"umbrellaName":null,"ratio":"100%"}]
def get_secid_paramlist(secid):
    url = 'http://dcweb613/GED/Sec/searchSECInvestByParams.action'
    data = {
        "form.searchType": "ShareId",
        "form.parameter": secid,
        "page.page": 1,
        "page.rp": 100
    }
    req = requests.get(url, timeout=300, params=data)
    return req.json()['parameterList']


# 当传入一个SecId时请向secid传入一个字符串，当传入多个SecId时请向secid传入一个list
# {'form': {'activeOnly': None, 'countries': None, 'country': None, 'cusip': None, 'deleteInvestmentIds': None, 'fundIds': None, 'investType': None, 'isin': None, 'legalName': None, 'legalNames': None, 'lstInvestInfo': None, 'lstSelected': None, 'masterRecordId': None, 'operationType': None, 'parameter': None, 'partnerId': None, 'processId': '44786843', 'providerIds': None, 'searchType': 'ShareId', 'secId': None, 'secIds': None, 'secName': None, 'status': None, 'symbol': None, 'tickerId': None, 'totalCount': None, 'tradingTicker': None, 'umbrella': None, 'umbrellaIds': None, 'universe': None, 'universes': None, 'updateUser': '1018'}, 'fundName': None, 'investmentList': None, 'jsonString': '[{"dictionaryId": null, "order": 0, "page": "1", "rows": [{"check": true, "fundId": "FSUSA001T7", "investmentId": "F000005GSN", "investmentName": "Salient International Small Cap Advisor", "investmentType": 1, "legalName": "Salient International Small Cap Fund Class Advisor", "matchRatio": 100.0, "parentValue": "F000005GSN", "providerId": "0C00009CAB", "providerName": "Salient Funds", "status": 0, "total": 1, "umbrellaId": null, "umbrellaName": null}], "total": 1, "value": "F000005GSN"}]', 'metaData': None, 'page': None, 'parameterList': None, 'rawFundCount': None, 'searchKey': None, 'selected': None, 'success': True}
def add_mapping(userid, processid, secid):
    if isinstance(secid, str) is True:
        json_str = json.dumps(get_secid_paramlist(secid))
        url = 'http://dcweb613/GED/Sec/updateSECInvestMapping.action'
        data = {
            "form.updateUser": userid,
            "form.processId": processid,
            "form.searchType": "ShareId",
            "jsonString": json_str
        }
        req = requests.get(url, timeout=300, params=data)
        # runQC(userid,processid)
        return req.json()
    elif isinstance(secid, list) is True:
        try:
            for each_secid in secid:
                json_str = json.dumps(get_secid_paramlist(each_secid))
                url = 'http://dcweb613/GED/Sec/updateSECInvestMapping.action'
                data = {
                    "form.updateUser": userid,
                    "form.processId": processid,
                    "form.searchType": "ShareId",
                    "jsonString": json_str
                }
                req = requests.get(url, timeout=300, params=data)
                return_info = req.json()['success']
                while return_info is False:
                    req = requests.get(url, timeout=300, params=data)
                    return_info = req.json()['success']
                    time.sleep(0.5)
            # runQC(userid,processid)
            return json.loads(json.dumps({'success': True}))
        except:
            return json.loads(json.dumps({'success': False}))


# 当传入一个SecId时请向secid传入一个字符串，当传入多个SecId时请向secid传入一个list
# {'form': {'activeOnly': None, 'countries': None, 'country': None, 'cusip': None, 'deleteInvestmentIds': 'FOUSA00G5E', 'fundIds': None, 'investType': None, 'isin': None, 'legalName': None, 'legalNames': None, 'lstInvestInfo': None, 'lstSelected': None, 'masterRecordId': None, 'operationType': None, 'parameter': None, 'partnerId': None, 'processId': '47076425', 'providerIds': None, 'searchType': None, 'secId': None, 'secIds': None, 'secName': None, 'status': None, 'symbol': None, 'tickerId': None, 'totalCount': None, 'tradingTicker': None, 'umbrella': None, 'umbrellaIds': None, 'universe': None, 'universes': None, 'updateUser': '601'}, 'fundName': None, 'investmentList': None, 'jsonString': None, 'metaData': None, 'page': None, 'parameterList': None, 'rawFundCount': None, 'searchKey': None, 'selected': None, 'success': True}
def del_mapping(userid, processid, secid):
    if isinstance(secid, str) is True:
        url = 'http://dcweb613/GED/Sec/deleteSECInvestMapping.action'
        data = {
            "form.deleteInvestmentIds": secid,
            "form.updateUser": userid,
            "form.processId": processid
        }
        req = requests.get(url, timeout=300, params=data)
        return req.json()
    elif isinstance(secid, list) is True:
        try:
            for each_secid in secid:
                url = 'http://dcweb613/GED/Sec/deleteSECInvestMapping.action'
                data = {
                    "form.deleteInvestmentIds": each_secid,
                    "form.updateUser": userid,
                    "form.processId": processid
                }
                req = requests.get(url, timeout=300, params=data)
                return_info = req.json()['success']
                while return_info is False:
                    req = requests.get(url, timeout=300, params=data)
                    return_info = req.json()['success']
                    time.sleep(0.5)
            return json.loads(json.dumps({'success': True}))
        except:
            return json.loads(json.dumps({'success': False}))


# {'accessionNumber': '0001162044-17-000630', 'category': 1, 'categoryName': 'USMF', 'cik': '1539935', 'comment': None, 'companyName': 'PSG CAPITAL MANAGEMENT TRUST', 'companyOwner': None, 'companyOwnerName': 'viki.chen', 'completeLinkTime': '2017-08-01 02:09:57.987', 'creationDate': '2017-07-27 21:29:23.33', 'documentDate': '2017-07-27', 'documentId': 139935781, 'documentType': '1', 'documentTypeName': 'Prospectus', 'effectiveDate': '2017-08-01', 'fileSize': 390346, 'filingId': 28496625, 'formType': '485BPOS', 'format': 'HTM', 'investmentId': None, 'investmentNum': 1, 'isTXT': None, 'owner': 0, 'processId': 44572481, 'qcnum': 0, 'r_TotalCount': 1, 'specialStatus': None, 'status': 10, 'statusName': 'Complete', 'updateDate': '2017-08-03 02:20:56.217', 'updateUserId': 1018, 'updateUserName': 'jeffrey.yu'}
def get_doc_meta(id, idtype='ProcessId'):
    if idtype == 'ProcessId':
        url = 'http://dcweb613/GED/Sec/findSECFundDocumentList.action'
        data = {
            "form.category": "",
            "form.docType": "",
            "form.status": "",
            "form.format": "",
            "form.filingId": "",
            "form.processId": id,
            "form.documentId": "",
            "form.formType": "",
            "form.accessionNumber": "",
            "form.cik": "",
            "form.from": "",
            "form.to": "",
            "form.cusip": "",
            "form.companyName": "",
            "form.investmentId": "",
            "form.specialStatus": "0",
            "form.policyId": ""
        }
        req = requests.get(url, timeout=300, params=data)
    else:
        url = 'http://dcweb613/GED/Sec/findSECFundDocumentList.action'
        data = {
            "form.category": "",
            "form.docType": "",
            "form.status": "",
            "form.format": "",
            "form.filingId": "",
            "form.processId": "",
            "form.documentId": id,
            "form.formType": "",
            "form.accessionNumber": "",
            "form.cik": "",
            "form.from": "",
            "form.to": "",
            "form.cusip": "",
            "form.companyName": "",
            "form.investmentId": "",
            "form.specialStatus": "0",
            "form.policyId": ""
        }
        req = requests.get(url, timeout=300, params=data)
    return req.json()['metaData']['rows'][0]


# {'accessionNumber': '0001193125-17-245399', 'category': 1, 'categoryName': 'USMF', 'cik': 889188, 'comment': None, 'companyName': 'Forward Funds', 'companyOwner': None, 'companyOwnerName': 'violet.cai', 'contractId': 'C000003323,C000003324,C000063087,C000082479', 'contractIdNum': 4, 'contractStatus': 0, 'contractStatusName': 'NonExists', 'docNum': 2, 'fileDate': '2017-08-02', 'fileSize': 55077, 'fileSizeName': '54KB', 'filingId': 29272395, 'formType': '497', 'isXBRL': None, 'isXBRLName': 'N', 'owner': 1223, 'profileId': 999, 'r_TotalCount': 1, 'status': 1, 'statusName': 'Doccreated', 'updateCategoryFlag': 1, 'updateDate': '2017-08-02 20:10:00.0', 'updateUserId': 1018, 'updateUserName': 'jeffrey.yu'}
def get_filing_meta(filingid):
    url = 'http://dcweb613/GED/Sec/findSECFilingList.action'
    data = {
        "form.category": "",
        "form.status": "",
        "form.fileDate": "",
        "form.cutter": "",
        "form.companyOwner": "",
        "form.cik": "",
        "form.accession": "",
        "form.filingId": filingid,
        "form.formType": "",
        "form.from": "",
        "form.to": "",
        "form.contractId": "",
        "form.companyName": ""
    }
    req = requests.get(url, timeout=300, params=data)
    return req.json()['metaData']['rows'][0]


# {'SECWebParameter': 'success', 'accessionNumber': None, 'cik': None, 'deleteDWDocResult': '', 'form': {'accessionNumber': None, 'category': None, 'cik': None, 'companyName': None, 'cusip': None, 'docType': None, 'documentId': None, 'filingId': None, 'formType': None, 'format': None, 'from': None, 'investmentId': None, 'policyId': None, 'processId': None, 'qcFilingId': None, 'qcProcessId': None, 'specialStatus': None, 'status': None, 'statusChangeType': 0, 'to': None, 'totalRow': 0, 'updateList': [{'documentId': 140333684, 'owner': 0, 'processId': 44786843, 'specialStatus': 0, 'status': 0}], 'updateUser': 1018}, 'metaData': None, 'page': None}
def junk_doc(userid, id, idtype='ProcessId'):
    if idtype == 'ProcessId':
        url = 'http://dcweb613/GED/Sec/batchUpdateDocumentStatus.action'
        data = {
            "form.updateUser":
            userid,
            "form.statusChangeType":
            "1",
            "form.updateList[0].processId":
            id,
            "form.updateList[0].documentId":
            get_doc_meta(id, idtype='ProcessId')['documentId']
        }
        req = requests.get(url, timeout=300, params=data)
    else:
        url = 'http://dcweb613/GED/Sec/batchUpdateDocumentStatus.action'
        data = {
            "form.updateUser":
            userid,
            "form.statusChangeType":
            "1",
            "form.updateList[0].processId":
            get_doc_meta(id, idtype='DocumentId')['processId'],
            "form.updateList[0].documentId":
            id
        }
        req = requests.get(url, timeout=300, params=data)
    return req.json()['SECWebParameter']


# {'form': {'accession': None, 'category': None, 'cik': None, 'cikName': None, 'companyName': None, 'companyOwner': None, 'contractId': None, 'cutter': None, 'fileDate': None, 'filingId': None, 'formType': None, 'from': None, 'owner': None, 'status': None, 'to': None, 'totalRow': 0, 'updateList': [{'category': None, 'cik': None, 'filingId': 29272395, 'owner': None, 'status': 5}], 'updateUser': 1018}, 'formTypes': None, 'metaData': None, 'page': None, 'secFilingService': {}}
def ignore_filing(userid, filingid):
    url = 'http://dcweb613/GED/Sec/batchUpdateFilingStatus.action'
    data = {
        "form.updateUser": userid,
        "form.updateList[0].filingId": filingid,
        "form.updateList[0].status": "5",
        "form.updateList[0].category": "",
        "form.updateList[0].cik": ""
    }
    req = requests.get(url, timeout=300, params=data)
    return req.json()


# # {"form":{"checker":null,"cutter":null,"documentId":null,"fixed":null,"from":"2017-08-01","processId":null,"to":"","totalRow":0,"trueDefect":null,"unAssigned":null,"updateList":null},"metaData":null,"page":null}
# def run_format():
#     startdate = (datetime.date.today() - datetime.timedelta(
#         days=7)).strftime('%Y-%m-%d')
#     url = 'http://dcweb613/GED/Sec/statisticalReport.action'
#     data = {"form.from": startdate, "form.to": ""}
#     req = requests.get(url, timeout=2000, params=data)
#     return req.json()


# # {'form': {'assignee': '988,1105,1104,1195,1202,1224,1223,1171', 'reportType': 1, 'updateList': [{'contractId': None, 'documentId': None, 'filingId': None, 'processId': 47596520}]}}
# def assign_format(userid, checker):
#     # userid = 601
#     # checker = '988,1105,1104,1171,1195,1202,1224,1223'
#     run_format()

#     url = 'http://dcweb613/GED/Sec/findFormatCheckReportList.action'
#     data = {
#         "form.fixed": "",
#         "form.unAssigned": "-1",
#         "form.from": "",
#         "form.to": "",
#         "form.processId": "",
#         "form.documentId": "",
#         "form.checker": "",
#         "form.cutter": "",
#         "form.trueDefect": "",
#         "page.page": "1",
#         "page.rp": "10000",
#         "page.sortname": "processId",
#         "page.sortorder": "desc",
#         "page.query": "",
#         "page.qtype": ""
#     }
#     req = requests.get(url, timeout=2000, params=data)
#     record_list = req.json()['metaData']['rows']
#     data_assign = {
#         "form.updateUser": userid,
#         "form.reportType": "1",
#         "form.assignee": checker
#     }
#     if len(record_list) > 100:
#         for i in range(0, len(record_list), 100):
#             new_record_list = record_list[i:i + 100]
#             for each in new_record_list:
#                 data_assign['form.updateList['
#                             + str(new_record_list.index(each)) +
#                             '].processId'] = each['processId']
#             url_assign = 'http://dcweb613/GED/Sec/assignCheckerReport.action'
#             req_assign = requests.get(
#                 url_assign, timeout=2000, params=data_assign)
#         return req_assign.json()
#     elif len(record_list) == 0:
#         return 'No Document.'
#     else:
#         for each in record_list:
#             data_assign['form.updateList[' + str(record_list.index(each)) +
#                         '].processId'] = each['processId']
#         url_assign = 'http://dcweb613/GED/Sec/assignCheckerReport.action'
#         req_assign = requests.get(url_assign, timeout=2000, params=data_assign)
#         return req_assign.json()


# {"ciks":null,"docModel":null,"documentAPIService":{"timeOut":1800000},"exist":false,"existsNoCDocSecId":null,"form":{"categoryId":null,"cik":null,"companyName":null,"companyOwner":null,"contractIds":null,"contractName":null,"creationDateFrom":null,"creationDateTo":null,"currentProcessId":45823606,"docList":null,"documentIds":null,"documentType":null,"existedDoc":null,"filingIds":null,"firstOpen":null,"formType":null,"investmentIds":null,"isCurrentDoc":null,"mappingRule":null,"newInvstmentLst":null,"owner":null,"processIds":"33741023","qcRuleId":null,"status":null,"updateUserId":1018},"investModel":null,"investmentProcessModel":null,"metaData":{"page":"1","rows":[{"cik":null,"contractId":null,"matchedCount":6,"unmatchedCount":0}],"total":1},"metaDocData":null,"model":null,"page":{"page":null,"qtype":null,"query":null,"rp":"100","sortname":null,"sortorder":null},"secDocumentRootPath":"\/data\/app\/mount\/edgar\/doc","timeLogModel":null}
def import_doc_mapping(userid, target_processid, origin_processid):
    url = 'http://dcweb613/GED/Sec/importSECMappingById.action'
    data = {
        "form.processIds": origin_processid,
        "form.updateUserId": userid,
        "form.currentProcessId": target_processid
    }
    req = requests.get(url, timeout=2000, params=data)
    return req.json()


# {"cikChartModel":null,"ciks":null,"docModel":null,"documentAPIService":{"timeOut":1800000},"exist":false,"existsNoCDocSecId":null,"form":{"categoryId":null,"chartCIK":null,"chartDocumentType":null,"cik":null,"companyName":null,"companyOwner":null,"contractIds":null,"contractName":null,"creationDateFrom":null,"creationDateTo":null,"currentProcessId":46235422,"docList":null,"documentIds":null,"documentType":null,"existedDoc":null,"filingIds":"34606285","firstOpen":null,"formType":null,"investmentIds":null,"isCurrentDoc":null,"mappingRule":null,"needChart":null,"newInvstmentLst":null,"owner":null,"processIds":null,"qcRuleId":null,"status":null,"updateUserId":1018},"investModel":null,"investmentProcessModel":null,"metaData":{"page":"1","rows":[{"cik":null,"contractId":null,"matchedCount":4,"unmatchedCount":0}],"total":1},"metaDocData":null,"model":null,"page":{"page":null,"qtype":null,"query":null,"rp":"100","sortname":null,"sortorder":null},"secDocumentRootPath":"\/data\/app\/mount\/edgar\/doc","timeLogModel":null}
def auto_mapping(userid, processid):
    filingid = get_doc_meta(processid, idtype='ProcessId')['filingId']
    url = 'http://dcweb613/GED/Sec/importSECMappingById.action'
    data = {
        "form.filingIds": filingid,
        "form.updateUserId": userid,
        "form.currentProcessId": processid
    }
    req = requests.get(url, timeout=2000, params=data)
    return req.json()
