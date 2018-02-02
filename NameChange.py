import re
import threading
import pandas as pd
import pyodbc
import requests
from bs4 import BeautifulSoup
import common


# def get_filing(processid, connection):
#     code = '''
#     select Comment,mp.ContainerId as filingid
#     from DocumentAcquisition..MasterProcess as mp
#     where mp.Category=1
#     and mp.ProcessId=%s
#         ''' % (processid)
#     cursor = connection.cursor()
#     result = cursor.execute(code).fetchall()
#     comment_result = result[0][0]
#     filingid = result[0][1]

#     if comment_result is not None:
#         regex = re.compile('\d{8}') # 会随着时间的改变而改变
#         duplicat_result = re.findall(regex, comment_result)
#         duplicat_result.append(str(filingid))
#         filingid_list = list(set(duplicat_result))
#     else:
#         filingid_list = [str(filingid)]
#     return filingid_list


def get_filing(processid):
    url = 'http://dcweb613/GED/Sec/findSECFundDocumentList.action'
    data = {
            "form.category": "",
            "form.docType": "",
            "form.status": "",
            "form.format": "",
            "form.filingId": "",
            "form.processId": processid,
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
    request = requests.get(url, timeout=300, params=data)
    json_result = request.json()['metaData']['rows'][0]
    comment = json_result['comment']
    filingid = str(json_result['filingId'])

    if comment is not None:
        regex = re.compile('\d{8}')
        duplicate_filing = re.findall(regex, comment)
        duplicate_filing.append(filingid)
        filingid_list = list(set(duplicate_filing))
    else:
        filingid_list = [filingid]
    return filingid_list


def get_doc(connection, filingid_list):
    docid_list = []
    for filing in filingid_list:
        code = '''
                select distinct sd.DocumentId
                from DocumentAcquisition..SECFiling as secf
                left join DocumentAcquisition..FilingSECContract as fs on fs.FilingId=secf.FilingId
                left join DocumentAcquisition..SECFiling as secf1 on secf1.CIK=fs.CIK
                left join DocumentAcquisition..MasterProcess as mp on mp.ContainerId=secf1.FilingId
                left join DocumentAcquisition..InvestmentMapping as im on im.ProcessId=mp.ProcessId
                left join SecurityData..SecuritySearch as ss on ss.SecId=im.InvestmentId
                left join DocumentAcquisition..SECCurrentDocument as sd on sd.InvestmentId=ss.SecId
                --left join DocumentAcquisition..SystemParameter as sp on sp.CodeInt=sd.DocumentType and sp.CategoryId=105
                where mp.Category=1 and mp.Status<>5 and mp.Format<>'PDF' and ss.Status in (1,2) 
                and sd.DocumentId is not null and mp.CreationDate>=GETDATE()-180 and sd.DocumentType=2
                and secf.FilingId in (%s)
                ''' % (filing)
        cursor = connection.cursor()
        result = cursor.execute(code).fetchall()
        for i in result:
            docid_list.append(i[0])
    docid_list = list(set(docid_list))
    return docid_list


def get_content(docid):
    url = 'http://doc.morningstar.com/document/%s.msdoc/?clientid=gfdt&key=9afafb2e67d38883' % (docid)
    req = requests.get(url, timeout=300)
    req.encoding='utf-8'
    soup =BeautifulSoup(req.text, 'lxml')
    content_text = soup.getText().replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    return content_text


def name_change(range_start, range_end, num, filing_list, docid_list, keywords, total_result):
    for i in range(range_start, range_end):
        if i < num:

            docid = docid_list[i]
            content = get_content(docid)
            if keywords in content:
                keywords_num = content.count(keywords)
                result = [str(docid), keywords, str(keywords_num)]
                total_result.append(result)
            else:
                # result = [str(docid), keywords, '0']
                pass
                
    return total_result


def run_result(processid, keywords):
    connection = pyodbc.connect(common.connection_string_multithread)

    filing_list = get_filing(processid)
    docid_list = get_doc(connection, filing_list)
    mutex = threading.Lock()

    if len(docid_list) == 0:
        total_result = []
    else:
        total_result = []
        total_thread = 10
        num = len(docid_list)

        if num < 10:
            total_thread = num
        
        gap = int(float(num/total_thread))
        

        thread_list = [threading.Thread(target=name_change, args=(i, gap+i, num, filing_list, docid_list, keywords, total_result,)) for i in range(0, num, gap)]
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        for i in thread_list:
            i.join()

    html_code = '''
                <!DOCTYPE HTML>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <link rel="shortcut icon" href="/static/img/Favicon.ico" type="image/x-icon"/>
                        <title>Name Chnage</title>
                    </head>
                    <body>
                    <h3>Name Change</h3>
                '''

    html_code = html_code + 'Key Words:  ' + keywords + '<br/><br/>'

    html_table = '''
                <table border="1" class="tablestyle">
                <thead>
                <tr style="text-align: right;">
                    <th>No</th>
                    <th>DocumentId</th>
                    <th>KeyWords</th>
                    <th>KeyWordsNum</th>
                    </tr>
                </thead>
                <tbody>
                ''' 
    html_code = html_code + html_table

    if total_result == []:
        html_code = html_code + '</tbody></table></body></html>'
        html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle" target="_blank"></a></td>')
    else:
        for row in range(len(total_result)):
            html_code = html_code + '<tr><td>%s</td>' % str(row + 1)
            for column in range(3):
                if column == 0:
                    html_code = html_code + '<td><a href="http://doc.morningstar.com/document/%s.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b"  target="_blank"> %s </a></td>' % (total_result[row][column], total_result[row][column])
                else:
                    html_code = html_code + '<td>%s</td>' % (total_result[row][column])

        html_code = html_code + '</tr>'
        html_code = html_code + '</tbody></table></body></html>'
        html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')
    
    return html_code

# processid = 51698295
# keywords = 'This Supplement should be retained'

# a = run_result(processid, keywords)
# print(a)