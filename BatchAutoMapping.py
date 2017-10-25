#!/usr/bin/env python
# -*- coding: utf-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/05 15:09
#--RevisedDate:   2017/10/25
#------------------------------------

import datetime
import smtplib
from email.header import Header
from email.mime.text import MIMEText
import DAP_API as dap
import common


def convert_processid(x):
    x = str(x)
    pid_list = []
    pids1 = x.split('\n')
    for line in pids1:
        line = line.strip('\n')
        line = line.strip('\r')
        pid_list.append(line)
    return pid_list


def send_mail(ip, content):
    with open('C:\\AutoNotification\\to_addr_list.txt', 'r') as toaddr:
        to_addr = [line.strip() for line in toaddr]
    # to_addr = ['Jeffrey.Yu@morningstar.com']
    from_addr = 'China.USDocument@morningstar.com'
    msg = MIMEText(content,'html')
    msg['To'] = ','.join(to_addr)
    msg['Subject'] = Header('Batch Auto Mapping Log from ' + str(ip), 'utf-8').encode()
    server = smtplib.SMTP('smtp.morningstar.com', 587)
    server.starttls()
    server.login('ChinaUSDocument', 'yAq1ZwK1')
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def run(pids, runqc, mapper, user_request):
    try:
        ip = common.get_IP(user_request)
        if runqc == '1':
            comment = '<b><font size="10" color="red">Warning!</font></b><br/><br/>The mapping operator is from ' + str(ip) + '<br/><br/>The below document(s) were mapped <b>successfully</b> and it would be <b>completed</b>. You can check the ProcessId(s) below: <br/>'
        else:
            comment = '<b><font size="10" color="red">Warning!</font></b><br/><br/>The mapping operator is from ' + str(ip) + '<br/><br/>The below document(s) were mapped <b>successfully</b> and it would <b>keep current status</b>. You can check the ProcessId(s) below: <br/>'
        processid_list = convert_processid(pids)
        for processid in processid_list:
            try:
                dap.auto_mapping(mapper,processid)
                if runqc == '1':
                    dap.runQC(mapper,processid)
                comment = comment + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '   ——→   ' + str(processid) + '<br/>'
            except Exception as e1:
                comment = comment + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '   ——→   ' + str(processid) + ' <b><font size="5" color="red">Failed!</font></b> Error: ' + str(e1) + '<br/>'
        comment += '<br/>------End------<br/>'
        send_mail(ip, comment)
        return comment
    except Exception as e:
        return str(e)