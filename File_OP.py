#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# ------------------------------------
# --Author:        Jeffrey Yu
# --CreationDate:  2017/09/14
# --RevisedDate:   2017/10/12
# ------------------------------------

import os
import shutil
import zipfile
import pyodbc
import tempfile
import requests
import re
import codecs
import html
import html2text
from bs4 import BeautifulSoup


def upzip(file_path):
    zip_file = zipfile.ZipFile(file_path)
    if os.path.isdir(file_path[:-4] + '\\'):
        pass
    else:
        os.mkdir(file_path[:-4] + '\\')
    for names in zip_file.namelist():
        zip_file.extract(names, file_path[:-4] + '\\')
    zip_file.close()


def get_filing_path(connection, filingid):
    code = '''
        select f.FilingId,f.AccessionNumber,f.CIK
        from DocumentAcquisition..SECFiling f
        where f.FilingId=%s
        ''' % (filingid)
    cursor = connection.cursor()
    cursor.execute(code)
    result = cursor.fetchall()
    if len(result) > 0:
        filing_path = '\\\\dcptprdapp1004\\DataManagerXML\\SEC\\Filing\\edgar\\data\\' + str(
            result[0][2])[:-4] + '0000\\' + str(result[0][2]) + '\\' + str(
                result[0][1]) + '.zip'
    cursor.close()
    return [filingid, result[0][1], result[0][2], filing_path]


def get_doc_server_path(connection, processid):
    code = '''
        select FileName from DocumentAcquisition..MasterProcess where ProcessId=%s
    ''' % (processid)
    cursor = connection.cursor()
    cursor.execute(code)
    result = cursor.fetchall()[0][0].replace('/', '\\')
    doc_path = '\\\\dcptprdapp1004\\DataManagerXML\\SEC\\Filing\\edgar\\doc\\' + result
    cursor.close()
    return doc_path


# source填DAP或SEC
def get_filing(filingid, source='DAP'):
    connection_string = 'Driver={SQL Server Native Client 10.0};Server=dcdrdb601\dminputdb;Database=DocumentAcquisition;Uid=jyu2;Pwd=hhh;Trusted_Domain=msdomain1;Trusted_Connection=yes;MARS_Connection=yes;'
    connection = pyodbc.connect(connection_string)

    if source == 'DAP':
        temp_folder = tempfile.mkdtemp()
        # print(temp_folder)
        temp_path = temp_folder + '\\' + str(filingid) + '\\'
        os.mkdir(temp_path)

        filing_info = get_filing_path(connection, filingid)
        AccessionNumber = filing_info[1]
        CIK = filing_info[2]
        filing_path = filing_info[3]

        temp_zip_file_path = temp_path + AccessionNumber + '.zip'
        shutil.copy2(filing_path, temp_zip_file_path)
        upzip(temp_zip_file_path)

        temp_filing_folder = temp_path + AccessionNumber + '\\'
        f_list = os.listdir(temp_filing_folder)
        html_name = ''
        for i in f_list:
            if os.path.splitext(i)[1] == '.html' or os.path.splitext(
                    i)[1] == '.htm':
                if '.head.' not in os.path.splitext(i)[0]:
                    html_name = i
        filing_html_path = temp_filing_folder + html_name
        with codecs.open(
                filing_html_path, 'r', encoding='UTF-8',
                errors='ignore') as html_reader:
            html_code = html_reader.read()
        connection.close()
        shutil.rmtree(temp_folder)
        return html_code
    else:
        filing_info = get_filing_path(connection, filingid)
        AccessionNumber = filing_info[1]
        CIK = filing_info[2]
        url = 'http://www.sec.gov/Archives/edgar/data/' + str(
            CIK) + '/' + AccessionNumber + '-index.htm'
        response = requests.get(url, timeout=300)
        response.encoding = 'UTF-8'
        page1 = response.text
        page2_reg = re.compile('<td scope="row"><a href="(.+?)"')
        page2_url = 'http://www.sec.gov' + page2_reg.findall(page1)[0]
        response = requests.get(page2_url, timeout=300)
        response.encoding = 'UTF-8'
        html_code = response.text
        return html_code


# idtype填ProcessId或者DocumentId；source填DAP或MDL
def get_doc(id, idtype='ProcessId', source='DAP'):
    connection_string = 'Driver={SQL Server Native Client 10.0};Server=dcdrdb601\dminputdb;Database=DocumentAcquisition;Uid=jyu2;Pwd=hhh;Trusted_Domain=msdomain1;Trusted_Connection=yes;MARS_Connection=yes;'
    connection = pyodbc.connect(connection_string)

    if idtype == 'ProcessId':
        code = '''
            select DocumentId from DocumentAcquisition..MasterProcess where ProcessId=%s
        ''' % (id)
        cursor = connection.cursor()
        cursor.execute(code)
        docid = cursor.fetchall()[0][0]
    else:
        code = '''
            select ProcessId from DocumentAcquisition..MasterProcess where DocumentId=%s
        ''' % (id)
        cursor = connection.cursor()
        cursor.execute(code)
        docid = id
        id = cursor.fetchall()[0][0]

    if source == 'MDL':
        url = 'http://doc.morningstar.com/document/' + str(
            docid
        ) + '.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b'
        response = requests.get(url, timeout=300)
        response.encoding = 'UTF-8'
        return response.text
    else:
        temp_folder = tempfile.mkdtemp()
        temp_path = temp_folder + '\\' + str(id) + '\\'
        os.mkdir(temp_path)

        zip_path = get_doc_server_path(connection, id)
        zip_file_name = zip_path.split('\\')[-1]

        temp_zip_file_path = temp_path + zip_file_name
        shutil.copy2(zip_path, temp_zip_file_path)
        upzip(temp_zip_file_path)
        new_doc_temp_path = temp_zip_file_path[:-4]
        f_list = os.listdir(new_doc_temp_path)
        html_name = ''
        for i in f_list:
            if os.path.splitext(i)[1] == '.html' or os.path.splitext(
                    i)[1] == '.htm':
                html_name = i
        html_doc_path = new_doc_temp_path + '\\' + html_name
        with open(
                html_doc_path, 'r', encoding='UTF-8',
                errors='ignore') as html_reader:
            html_code = html_reader.read()
        connection.close()
        shutil.rmtree(temp_folder)
        return html_code


# source填DAP或SEC；method填1或者2或者3，1是用html2text处理，2是用BeautifulSoup内置的get_text()处理，3是用BeautifulSoup提取文本再用join进行组合。
def get_filing_conent(filingid, source='DAP', method=1):
    html_code = html.unescape(get_filing(filingid, source=source))
    if method == 1:
        text_maker = html2text.HTML2Text()
        text_maker.ignore_tables = True
        text_maker.re_unescape = True
        text_maker.ignore_emphasis = True
        text_maker.body_width = 0
        content_text = text_maker.handle(html.unescape(html_code))
        content_text = html.unescape(content_text).replace('\n', '').replace('\r', '').replace('\t', '')
    elif method == 2:
        soup = BeautifulSoup(html_code, 'lxml')
        content_text = soup.get_text().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        content_text = re.sub('\\s+', ' ', content_text)
    elif method == 3:
        content_text = ''.join(BeautifulSoup(html_code, 'lxml').findAll(text=True)).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        content_text = re.sub('\\s+', ' ', content_text)
    return content_text


# idtype填ProcessId或者DocumentId；source填DAP或MDL；method填1或者2或者3，1是用html2text处理，2是用BeautifulSoup内置的get_text()处理，3是用BeautifulSoup提取文本再用join进行组合。
def get_doc_conent(id, idtype='ProcessId', source='DAP', method=1):
    html_code = html.unescape(get_doc(id, idtype=idtype, source=source))
    if method == 1:
        text_maker = html2text.HTML2Text()
        text_maker.ignore_tables = True
        text_maker.re_unescape = True
        text_maker.ignore_emphasis = True
        text_maker.body_width = 0
        content_text = text_maker.handle(html.unescape(html_code))
        content_text = html.unescape(content_text).replace('\n', '').replace('\r', '').replace('\t', '')
    elif method == 2:
        soup = BeautifulSoup(html_code, 'lxml')
        content_text = soup.get_text().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        content_text = re.sub('\\s+', ' ', content_text)
    elif method == 3:
        content_text = ''.join(BeautifulSoup(html_code, 'lxml').findAll(text=True)).replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        content_text = re.sub('\\s+', ' ', content_text)
    return content_text
