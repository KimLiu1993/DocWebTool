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


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)