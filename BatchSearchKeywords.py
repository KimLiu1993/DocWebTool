#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------
#--Author:        Sharol Liu
#--CreationDate:  2017/12/18
#--RevisedDate:   2018/03/29
#------------------------------------


import re
import os
import time
import threading
import requests
import pandas as pd
import File_OP as fo
import DAP_API as api
import common


# 获取docid在MDL上的doc
def get_doc(docid):
    docid = str(docid)
    url = 'http://doc.morningstar.com/document/' + docid + '.msdoc/?clientid=gfdt&key=9afafb2e67d38883'
    req = requests.get(url, timeout=300)
    return req


# 获取有ProcessId、没DocId的non-us的doc
def get_no_docid_doc(processid):
    url = 'http://dcweb613/GED/openFilingByProcessId.action?form.processId={}'.format(processid)
    response = requests.get(url, timeout=300)
    return response


# 根据ProcessId获得对应的DocumentId
def get_docid_from_processid(id):
    try:
        url_api = 'http://dcdocstgap8001:8080/SqlPassAPI/controller/sql?sqlId=46&params={}'.format(id)
        req = requests.get(url_api, timeout=300)
        docid = req.json()['result'][0]['DocumentId']
    except:
        try:
            url_nus = 'http://dcweb613/GED/Fund/searchFundMeta.action'
            data_nus = {
                "form.market": "",
                "form.docDateBegin": "",
                "form.docDateEnd": "",
                "form.investment": "",
                "form.processId": str(id),
                "form.source": "",
                "form.effDateBegin": "",
                "form.effDateEnd": "",
                "form.documentId": "",
                "form.profileId": "",
                "form.specialStatus": "",
                "form.internalOnly": "",
                "form.docType": "",
                "form.subDocType": "",
                "form.language": "",
                "form.status": "",
                "form.containerId": "",
                "form.sender": "",
                "form.priority": "",
                "form.age": "",
                "form.daId": "",
                'page.page': "1",
                'page.rp': "100",
                'page.sortname': "processId",
                'page.sortorder': "asc",
                'page.query': "",
                'page.qtype': ""
            }
            req = requests.get(url_nus, timeout=300, params=data_nus)
            docid = req.json()['metaData']['rows'][0]['documentId']
        except IndexError:
            docid = api.get_doc_meta(id, idtype='ProcessId')['documentId']
    return docid


# 获取docid在MDL上的源代码，并识别formattype
def get_doc_type(x):
    if x.headers['Content-Type'] == 'application/pdf':
        return 'PDF'
    else:
        x = str(x.text)
        string = re.findall(re.compile('MS_RAW.*\.htm'), x)
        if len(string) > 0:
            return 'HTML'
        else:
            string = re.findall(re.compile('MS_RAW.*\.txt'), x)
            if len(string) > 0:
                return 'TXT'
            else:
                return 'HTML'


# 获取filingid在SEC上的内容，并识别formattype
def get_filing_type(x):
    string = re.findall(re.compile('<FILENAME>.*'), x)[0]
    if '.txt' in string:
        return 'TXT'
    else:
        return 'HTML'


# 若keywordtype为字符串，只统计关键词出现次数，若keywordtype为正则表达式，则统计符合正则表达式的字符串数，并列出所有字符串
def keyword_count(Id, kw_list, keywordtype, content, formtype):
    result = []
    for keyword in kw_list: 
        if keyword != '':
            if content == '':
                result_num = 0
                each_result = [Id + '(Cannot parse)', keyword, result_num, formtype, '']
                result.append(each_result)
            else:
                if keywordtype == 'string':
                    # re_keyword = re.compile(keyword, re.IGNORECASE)
                    # result_list = re.findall(keyword.lower(), content.lower())
                    # result_num = len(result_list)
                    result_num = content.lower().count(keyword.lower())
                    each_result = [Id, keyword, result_num, formtype, '']
                else:
                    regex = re.compile(keyword)
                    result_list = re.findall(regex, content)
                    result_num = len(result_list)
                    each_result = [Id, keyword, result_num, formtype, result_list]
                result.append(each_result)
        else:
            pass
    return result


# 利用pdftotext.exe将pdf转存为txt,并返回txt内容
def get_pdf_text(docid,file):
    pdftotext = common.cur_file_dir() + '\\static\\pdftotext.exe'
    output = common.cur_file_dir() + '\\temp\\' + docid + '.txt'
    cmd = pdftotext + ' -raw -enc UTF-8 ' + file + ' ' + output
    os.system(cmd)
    time.sleep(2)
    try:
        with open(output,'r',encoding='UTF-8') as text_reader:
            text = text_reader.read()
    except:
        time.sleep(5)
        try:
            with open(output, 'r', encoding='UTF-8') as text_reader:
                text = text_reader.read()
        except:
            text = ''
    if os.path.isfile(output):
        os.remove(output)
    return text    


# documenttype为document查找关键词的函数
def search_keyword_doc(docid, doc_data, kw_list, keywordtype, formtype):
    if formtype == 'PDF':
        with open(common.cur_file_dir() + '\\temp\\' + str(docid) + '.pdf', 'wb') as f:
            f.write(doc_data)
        doc_text = get_pdf_text(docid, common.cur_file_dir() + '\\temp\\' + str(docid) + '.pdf')
        result = keyword_count(docid, kw_list, keywordtype, doc_text, formtype)

        if os.path.isfile(common.cur_file_dir() + '\\temp\\' + str(docid) + '.pdf'):
            os.remove(common.cur_file_dir() + '\\temp\\' + str(docid) + '.pdf')
        return result
    elif formtype == 'HTML':
        doc_text = fo.get_doc_conent(docid, idtype='DocumentId', source='MDL', method=2)
        result = keyword_count(docid, kw_list, keywordtype, doc_text, formtype)
        return result
    else: # txt
        doc_text = str(doc_data)
        result = keyword_count(docid, kw_list, keywordtype, doc_text, formtype)
        return result


# documenttype为filing查找关键词的函数
def search_keyword_filing(filingid, filing_data, kw_list, keywordtype, formtype):
    if formtype == 'HTML':
        filing_text = fo.get_filing_conent(filingid, source='SEC', method=2)
        result = keyword_count(filingid, kw_list, keywordtype, filing_text, formtype)
        return result
    else:
        result = keyword_count(filingid, kw_list, keywordtype, filing_data, formtype)
        return result


# 查找关键词的主要函数，分为document和filing
def search_keyword(Id, idtype, keyword_list, keywordtype, workernumber, mutex, total_result):
    if idtype == 'document' or idtype == 'process':
        if idtype == 'document':
            Id = Id
        else:
            Id = get_docid_from_processid(Id)
        if Id == 0 and idtype == 'process':
            doc = get_no_docid_doc(Id)
            formtype = 'PDF'
        else:
            doc = get_doc(Id)
            formtype = get_doc_type(doc)
        if formtype == 'TXT':
            result_list = search_keyword_doc(Id, doc.text, keyword_list, keywordtype, formtype)  
        else:
            result_list = search_keyword_doc(Id, doc.content, keyword_list, keywordtype, formtype)
    # elif idtype == 'process':

    else:
        filing = fo.get_filing(Id, source='SEC')
        filingtype = get_filing_type(filing)
        result_list = search_keyword_filing(Id, filing, keyword_list, keywordtype, filingtype)
        
    mutex.acquire()
    total_result.extend(result_list)
    mutex.release()


# 多线程的执行函数
def getrange(l, r, id_list, idtype, keyword_list, keywordtype, workernumber, mutex, total_result, num):
    for i in range(l, r):
        if i < num:
            Id = id_list[i]
            try:
                search_keyword(Id, idtype, keyword_list, keywordtype, workernumber, mutex, total_result)
            except:
                total_result.append([Id + ' (error)', ' ', ' ', ' ', ' '])

# 主函数
def run(ids, idtype, keywords, keywordtype, ThreadNumber):
    try:
        result_file = 'Reslut-' + time.strftime('%Y%m%d') + time.strftime('%H%M%S') + '.csv'
        result_path = common.cur_file_dir() + '\\Results\\'

        id_list = []
        ids1 = ids.split('\n')
        for line in ids1:
            if len(line) > 0:
                line = line.strip()
                line = line.strip('\r')
                id_list.append(line)

        keyword_list = []
        kw1 = keywords.split('\n')
        for line in kw1:
            if len(line) > 0:
                # line = line.strip()
                line = line.rstrip('\r')
                keyword_list.append(line)

        if not os.path.exists(result_path):
            os.makedirs(result_path)

        totalThread = ThreadNumber
        total_result = []

        num = len(id_list)
        if num < int(totalThread):
            totalThread = num
        gap = int(float(num) / float(totalThread))


        mutex = threading.Lock()
        threadlist = [threading.Thread(target=getrange, args=(i, i+gap, id_list, idtype, keyword_list, keywordtype, ThreadNumber, mutex, total_result, num,)) for i in range(0, num, gap)]
        for t in threadlist:
            t.setDaemon(True)
            t.start()
        for i in threadlist:
            i.join()


        df = pd.DataFrame(total_result, columns=['Id', 'KeyWord', 'Count', 'Format', ' '])

        try:
            if os.path.isfile(result_path + result_file):
                os.remove(result_path + result_file)
            df.to_csv(result_path + result_file, encoding='UTF-8')
        except:
            if os.path.isfile(result_path + result_file):
                os.remove(result_path + result_file)
            df.to_csv(result_path + result_file, encoding='GB18030')

        return (result_path, result_file)
    except Exception as e:
        return str(e)