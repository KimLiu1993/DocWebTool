#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/23 16:49
#--RevisedDate:   
#------------------------------------

import os
import random
import datetime
import subprocess
from bs4 import BeautifulSoup
import common
import File_OP as fo


def run(id1, id2):

    txt1_file = 'temp1-' + str(id1) + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000000, 9999999)) + '.txt'
    txt2_file = 'temp2-' + str(id2) + '-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(random.randint(1000000, 9999999)) + '.txt'

    exe_path = common.apps_path + 'BC\\BCompare.exe'
    txt1_path = common.temp_path + txt1_file
    txt2_path = common.temp_path + txt2_file
    BC_settings_path = common.apps_path + 'BC\\ToReport.txt'
    output_report_path = common.temp_path
    output_file = 'CompareReport-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.html'
    CMD = exe_path + ' /silent \"@' + BC_settings_path + '\" \"' + txt1_path + '\" \"' + txt2_path + '\" \"' + output_report_path + output_file + '\"'

    html1 = fo.get_doc(id1, idtype='ProcessId', source='DAP')
    soup1 = BeautifulSoup(html1, 'lxml')
    with open(txt1_path, 'w', encoding='UTF-8') as w1:
        w1.write(soup1.get_text())

    html2 = fo.get_doc(id2, idtype='ProcessId', source='DAP')
    soup2 = BeautifulSoup(html2, 'lxml')
    with open(txt2_path, 'w', encoding='UTF-8') as w2:
        w2.write(soup2.get_text())

    subprocess.call(CMD, shell=False)

    try:
        os.remove(txt1_path)
        os.remove(txt2_path)
    except:
        pass

    return output_report_path, output_file