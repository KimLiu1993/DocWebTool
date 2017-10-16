#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 10:53
#--RevisedDate:   
#------------------------------------

from flask import Flask, render_template, request, send_from_directory, send_file
import common

common.init()

app = Flask(__name__)


@app.route('/')
def homepage_show():
    return render_template('index.html')


@app.route('/mapbydocfromcik', methods=['POST'])
def mapbydocfromcik():
    return x


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)