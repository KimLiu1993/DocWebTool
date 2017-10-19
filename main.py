#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 10:53
#--RevisedDate:   2017/10/17
#------------------------------------

from flask import Flask, render_template, request, send_from_directory, send_file
import common
import IPTracking

common.init()

app = Flask(__name__)


@app.route('/')
def homepage_show():
    location_page = 'index.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/mapbydocfromcik', methods=['POST'])
def mapbydocfromcik():
    return x

@app.route('/doctracking')
def doctracking_show():
    visitor_ip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            visitor_ip = _ip
    except Exception as e:
        visitor_ip = visitor_ip
    tr.record(visitor_ip, 'doctracking')
    return render_template('doctracking.html')

@app.route('/doctracking', methods=['POST'])
def doctracking():
    idtype = str(request.form['idtype'])
    id_content = str(request.form['id'])
    timediff = str(request.form['timediff'])
    Uid = username
    Pwd = psw
    servername = str(request.form['servername'])
    dbname = str(request.form['dbname'])
    connection_string = 'Driver={SQL Server};Server=' + servername + ';Database=' + dbname + ';Uid=' + Uid + ';Pwd=' + Pwd + ';Trusted_Domain=msdomain1;Trusted_Connection=1;'
    
    import doctracking as dk
    if idtype == '1':
        processid = id_content
    else:
        processid = dk.get_processid(connection_string,id_content)
    return dk.run(connection_string,processid)



if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)