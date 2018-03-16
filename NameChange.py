import re
import threading
import pandas as pd
import pyodbc
import requests
from bs4 import BeautifulSoup
import common


# 通过contract id找最近一年的filing。
def contract_filing(connection, contractid):
    code = '''
            select fc.ContractId,fc.SeriesName,fc.ContractName,fc.CIK,fc.FilingId,fc.Accession,f.FormType,f.FileDate
            from DocumentAcquisition..FilingSECContract as fc
            left join DocumentAcquisition..SECFiling as f on f.FilingId=fc.FilingId
            where fc.ContractId='%s' and f.FileDate>GETDATE()-365
            order by fc.ContractId,f.FileDate desc
            ''' % (contractid)
    result = pd.read_sql(code, connection)
    return result


# 通过contract id找对应的secid
def get_secid(contractid, connection):
    cursor = connection.cursor()
    code = '''
            select InvestmentId
            from CurrentData..InvestmentIdentifier
            where IdentifierType=20 and Identifier='%s'
            ''' % (contractid)
    result = cursor.execute(code).fetchall()[0][0]
    return result


# 通过secid找对应的name change的记录。
def secid_name_change(connection, secid):
    cursor = connection.cursor()
    code = '''
            select ipnt.TrackingId, ipnt.InvestmentId as SecId, ipnt.Name as ShareName,
            ipnt.InvestmentType,ipnt.ActionType,ipnt.ActionTime as actiontime
            from LogData_DMWkspaceDB..InvestmentPreviousNameTracking as ipnt
            left join SupportData_DMWkspaceDB..UserSearch as us on us.UserId=ipnt.ActionUser
            where ipnt.InvestmentId='%s'
            union
            select distinct isnt.TrackingId,isnt.InvestmentId as secid,isnt.StandardName as sharename,isnt.InvestmentType,
            isnt.ActionType,isnt.ActionTime as actiontime
            from LogData_DMWkspaceDB..InvestmentStandardNameTracking as isnt
            left join SupportData_DMWkspaceDB..UserSearch as us1
            on us1.UserId=isnt.UserId
            where isnt.InvestmentId='%s'
            order by actiontime desc
            ''' % (secid, secid)
    result = pd.read_sql(code, connection)
    return result


# 通过secid找对应的current doc，doctype限于prospectus和supplement
def get_current_doc(connection, secid):
    cursor = connection.cursor()
    code = '''
            select distinct sd.DocumentId
            from SecurityData..SecuritySearch as ss
            left join DocumentAcquisition..SECCurrentDocument as sd on sd.InvestmentId=ss.SecId
            where ss.SecId='%s' and sd.DocumentType in(1,2)
        ''' % (secid)
    result = cursor.execute(code).fetchall()
    docid_list = [i[0] for i in result]
    return docid_list



def get_content(docid):
    url = 'http://doc.morningstar.com/document/%s.msdoc/?clientid=gfdt&key=9afafb2e67d38883' % (docid)
    req = requests.get(url, timeout=300)
    req.encoding='utf-8'
    soup =BeautifulSoup(req.text, 'lxml')
    content_text = soup.getText().replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    return content_text


def name_change(range_start, range_end, num, docid_list, keywords, total_result):
    for i in range(range_start, range_end):
        if i < num:
            docid = docid_list[i]
            content = get_content(docid)
            if keywords in content:
                keywords_num = content.count(keywords)
                result = [str(docid), keywords, str(keywords_num)]
                total_result.append(result)
            else:
                result = [str(docid), keywords, '0']
                total_result.append(result)                
    return total_result


def run_result(contractid, keywords):
    connection = pyodbc.connect(common.connection_string_multithread)
    secid = get_secid(contractid, connection)
    docid_list = get_current_doc(connection, secid)

    mutex = threading.Lock()

    # 得到含有关键词的结果
    if len(docid_list) == 0:
        total_result = []

    else:
        total_result = []
        total_thread = 5
        num = len(docid_list)
        if num < 5:
            total_thread = num
        
        gap = int(float(num/total_thread))
        thread_list = [threading.Thread(target=name_change, args=(i, gap+i, num, docid_list, keywords, total_result,)) for i in range(0, num, gap+1)]
        for t in thread_list:
            t.setDaemon(True)
            t.start()
        for i in thread_list:
            i.join()

    # 将所有结果以html的形式写出来
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

    # contractid_filing的结果
    html_code = html_code + 'ContractId: ' + contractid + '<br/><br/>'

    html_table1 = '''
                <table border="1" class="tablestyle">
                <thead>
                <tr style="text-align: right;">
                    <th>No</th>
                    <th>ContractId</th>
                    <th>SeriesName</th>
                    <th>ContractName</th>
                    <th>CIK</th>
                    <th>FilingId</th>
                    <th>Accession</th>
                    <th>FormType</th>
                    <th>FileDate</th>
                    </tr>
                </thead>
                <tbody>
                '''
    html_code = html_code + html_table1

    contract_result = contract_filing(connection, contractid)

    for row1 in range(len(contract_result)):

        html_code = html_code + '<tr><td>%s</td>' % str(row1 + 1)

        for column1 in range(8):
            if column1 == 5:
                html_code = html_code + '<td><a href="https://www.sec.gov/Archives/edgar/data/0/%s-index.htm" target="_blank">%s</a></td>' % (contract_result.iloc[row1, column1], contract_result.iloc[row1, column1])
            else:
                html_code = html_code + '<td>%s</td>' % (contract_result.iloc[row1, column1])
    html_code = html_code + '</tr></tbody></table><br/><br/>'

    # secid name change的结果
    html_code = html_code + 'SecId: ' + secid + '<br/><br/>'

    secid_result = secid_name_change(connection, secid)
    secid_result = secid_result.to_html(classes='tablestyle', index=False)
    
    html_code = html_code + secid_result + '<br/><br/>'

    # name change的关键词结果
    html_code = html_code + 'Key Words:  ' + keywords + '<br/><br/>'
    html_table3 = '''
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
    html_code = html_code + html_table3

    if total_result == []:
        html_code = html_code + '</tbody></table></body></html>'
        html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"', 'class="tablestyle" target="_blank"></a></td>')
    else:
        for row3 in range(len(total_result)):
            html_code = html_code + '<tr><td>%s</td>' % str(row3 + 1)
            for column3 in range(3):
                if column3 == 0:
                    html_code = html_code + '<td><a href="http://doc.morningstar.com/document/%s.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b"  target="_blank"> %s </a></td>' % (total_result[row3][column3], total_result[row3][column3])
                else:
                    html_code = html_code + '<td>%s</td>' % (total_result[row3][column3])

        html_code = html_code + '</tr>'
        html_code = html_code + '</tbody></table></body></html>'
        html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')
    return html_code    




    # html_code = '''
    #             <!DOCTYPE HTML>
    #                 <html>
    #                 <head>
    #                     <meta charset="utf-8">
    #                     <link rel="shortcut icon" href="/static/img/Favicon.ico" type="image/x-icon"/>
    #                     <title>Name Chnage</title>
    #                 </head>
    #                 <body>
    #                 <h3>Name Change</h3>
    #             '''

    # html_code = html_code + 'Key Words:  ' + keywords + '<br/><br/>'

    # html_table = '''
    #             <table border="1" class="tablestyle">
    #             <thead>
    #             <tr style="text-align: right;">
    #                 <th>No</th>
    #                 <th>DocumentId</th>
    #                 <th>KeyWords</th>
    #                 <th>KeyWordsNum</th>
    #                 </tr>
    #             </thead>
    #             <tbody>
    #             ''' 
    # html_code = html_code + html_table

    # if total_result == []:
    #     html_code = html_code + '</tbody></table></body></html>'
    #     html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle" target="_blank"></a></td>')
    # else:
    #     for row in range(len(total_result)):
    #         html_code = html_code + '<tr><td>%s</td>' % str(row + 1)
    #         for column in range(3):
    #             if column == 0:
    #                 html_code = html_code + '<td><a href="http://doc.morningstar.com/document/%s.msdoc/?clientid=uscomplianceserviceteam&key=617cf7b229240e1b"  target="_blank"> %s </a></td>' % (total_result[row][column], total_result[row][column])
    #             else:
    #                 html_code = html_code + '<td>%s</td>' % (total_result[row][column])

    #     html_code = html_code + '</tr>'
    #     html_code = html_code + '</tbody></table></body></html>'
    #     html_code = ('' + common.css_code + html_code).replace('class="dataframe tablestyle"','class="tablestyle"')
    
    # return html_code

# contractid = 'C000172618'
# keywords = 'approved or disapproved'

# a = run_result(contractid, keywords)
# print(a)