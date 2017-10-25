#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 10:53
#--RevisedDate:   2017/10/25
#------------------------------------

import os
import random
import datetime
from flask import Flask, render_template, request, send_from_directory, abort
import common
import IPTracking
import ContentCompare
import DocTracking as dt
import SearchByFundTicker
# import MapByDocFromCIK
import ContractIdFiling
import Rename
import Web_API

common.init()

app = Flask(__name__, static_url_path='')


@app.route('/')
def homepage_show():
    location_page = 'index.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/content')
def content_show():
    location_page = 'Content.html'
    IPTracking.log_IP(request, location_page)
    gif = random.randint(1, 2)
    if gif == 1:
        file_count = len([name for name in os.listdir(common.stickers_path) if os.path.isfile(os.path.join(common.stickers_path, name))])
        sticker_name = str(random.randint(1, file_count))
        return render_template(location_page, picname='/images/stickers/' + sticker_name + '.png')
    else:
        gif_path = common.stickers_path + 'gif\\'
        if not os.path.exists(gif):
            os.makedirs(gif)
        file_count = len([name for name in os.listdir(gif_path) if os.path.isfile(os.path.join(gif_path, name))])
        sticker_name = str(random.randint(1, file_count))
        return render_template(location_page, picname='/images/stickers/gif/' + sticker_name + '.gif')


@app.route('/hi')
def hi_show():
    location_page = 'Hi.html'
    IPTracking.log_IP(request, location_page)

    week_day_dict = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thursday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday',
    }

    today = datetime.datetime.now()
    today_str = today.strftime('%Y-%m-%d')

    week_day = datetime.datetime.now().weekday()
    weekday_str = week_day_dict[week_day]

    if week_day == 0:
        filingdate = (today - datetime.timedelta(days=3))

    elif week_day == 6:
        filingdate = (today - datetime.timedelta(days=2))
    else:
        filingdate = (today - datetime.timedelta(days=1))
    filingdate_str = filingdate.strftime('%Y-%m-%d')

    after60 = (filingdate + datetime.timedelta(days=60)).strftime('%Y-%m-%d')
    after75 = (filingdate + datetime.timedelta(days=75)).strftime('%Y-%m-%d')

    return render_template(location_page, today=today_str, weekday=weekday_str, filingdate=filingdate_str,
                           after60=after60, after75=after75)

@app.route('/maobydocfromcik')
def maobydocfromcik_show():
    location_page = 'MapByDocFromCIK.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/contentcompare')
def contentcompare_show():
    location_page = 'ContentCompare.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/doctracking')
def doctracking_show():
    location_page = 'DocTracking.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/contractidfiling')
def contractidfiling_show():
    location_page = 'ContractIdFiling.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/searchbyfundticker')
def searchbyfundticker_show():
    location_page = 'SearchByFundTicker.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/rename')
def rename_show():
    location_page = 'Rename.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/miumiu')
def miumiu_show():
    location_page = 'MiuMiu.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/elephant')
def elephant_show():
    location_page = 'Elephant.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/game1')
def game1_show():
    location_page = 'Game1.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/fruit_ninja')
def fruit_ninja_show():
    location_page = 'Fruit_ninja.html'
    IPTracking.log_IP(request, location_page)
    return app.send_static_file(location_page)


@app.route('/maobydocfromcik', methods=['POST'])
def maobydocfromcik():
    pass

@app.route('/contentcompare', methods=['POST'])
def contentcompare():
    try:
        id1 = str(request.form['id1'])
        id2 = str(request.form['id2'])
        result = ContentCompare.run(id1, id2)
        return send_from_directory(directory=result[0], filename=result[1])
    except Exception as e:
        return str(e)


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


@app.route('/contractidfiling', methods=['POST'])
def contractidfiling():
    contractid = str(request.form['contractid'])
    return ContractIdFiling.run_contractid(contractid)


@app.route('/searchbyfundticker', methods=['POST'])
def searchbyfundticker():
    regex = str(request.form['regex'])
    content = str(request.form['content'])
    return SearchByFundTicker.run(regex, content)


@app.route('/rename', methods=['POST'])
def rename():
    content = str(request.form['content'])
    result = Rename.run(content)
    return send_from_directory(directory=common.temp_path, filename=result, as_attachment=True)


@app.route('/api/v1.0/mapping', methods=['GET'])
def api_mapping():
    processid = request.args.get('processid')
    secid = request.args.get('secid')
    if processid is None or secid is None:
        abort(404, 'Wrong info was passed to API.')
    else:
        return_info = Web_API.mapping(request, processid, secid)
        return return_info


@app.route('/api/v1.0/importdocmapping', methods=['GET'])
def api_import_doc_mapping():
    from_processid = request.args.get('fromprocessid')
    to_processid = request.args.get('toprocessid')
    if from_processid is None or to_processid is None:
        abort(404, 'Wrong info was passed to API.')
    else:
        return_info = Web_API.mapping(request, processid, secid)
        return return_info


if __name__ == '__main__':
    # app.debug = True
    app.run(host='0.0.0.0', port=80, threaded=True)