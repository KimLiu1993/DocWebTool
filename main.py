#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 10:53
#--RevisedDate:   2017/10/19
#------------------------------------

from flask import Flask, render_template, request, send_from_directory, send_file
import common
import IPTracking
import DocTracking as dt

common.init()

app = Flask(__name__)


@app.route('/')
def homepage_show():
    location_page = 'index.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/doctracking')
def doctracking_show():
    location_page = 'DocTracking.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/doctracking', methods=['POST'])
def doctracking():
    idtype = str(request.form['idtype'])
    id_content = str(request.form['id'])
    timediff = str(request.form['timediff'])

    if idtype == '1':
        processid = id_content
    else:
        processid = dt.get_processid(id_content)
    return dt.run(processid, timediff)


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)