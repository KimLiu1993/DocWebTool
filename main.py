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
import Tracking_Record as tr

common.init()

app = Flask(__name__)


@app.route('/')
def homepage_show():
    location_page = 'index.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


# @app.route('/mapbydocfromcik', methods=['POST'])
# def mapbydocfromcik():
#     return x                            ??????

@app.route('/mapbydocfromcik')
def mapbydocfromcik_show():
    visitor_ip = request.remote_addr
    try:
        _ip = request.headers["X-Real-IP"]
        if _ip is not None:
            visitor_ip = _ip
    except Exception as e:
        visitor_ip = visitor_ip
    tr.record(visitor_ip, 'MapByDocFromCIK')
    return render_template('MapByDocFromCIK.html')

if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)