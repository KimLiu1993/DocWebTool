#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/16 10:53
#--RevisedDate:   2018/01/25
#------------------------------------

import os
import random
import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, request, send_from_directory, abort
import common
import IPTracking
import ContentCompare
import BatchAutoMapping
import DocTracking as dt
import SearchByFundTicker
import MapByDocFromCIK
import SearchContentFund
import ContractIdFiling
import Rename
import Web_API
import InternalAuditSampling
import BatchSearchKeywords
import MappingTool
import Timeliness
import NameChange
import VASubaccountCompare


#
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |// '.
#                 / \\|||  :  |||// \
#                / _||||| -:- |||||- \
#               |   | \\\  -  /// |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永无BUG


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

    return render_template(location_page, today=today_str, weekday=weekday_str, filingdate=filingdate_str, after60=after60, after75=after75)

@app.route('/mapbydocfromcik')
def maobydocfromcik_show():
    location_page = 'MapByDocFromCIK.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/searchcontentfund')
def searchcontentfund_show():
    location_page = 'SearchContentFund.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/internalauditsampling')
def internalauditsampling_show():
    location_page = 'InternalAuditSampling.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/contentcompare')
def contentcompare_show():
    location_page = 'ContentCompare.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/batchautomapping')
def batchautomapping_show():
    location_page = 'BatchAutoMapping.html'
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


@app.route('/namechange')
def namechange_show():
    location_page = 'NameChange.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/batchsearthkeywords')
def batchsearthkeywords_show():
    location_page = 'BatchSearchKeywords.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/searchbyfundticker')
def searchbyfundticker_show():
    location_page = 'SearchByFundTicker.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/mappingtool')
def mappingtool_show():
    location_page = 'MappingTool.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/vasubaccountcompare')
def vasubaccountcompare_show():
    location_page = 'VASubaccountCompare.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/rename')
def rename_show():
    location_page = 'Rename.html'
    IPTracking.log_IP(request, location_page)
    return render_template(location_page)


@app.route('/timeliness')
def timeliness_show():
    location_page = 'Timeliness.html'
    IPTracking.log_IP(request, location_page)
    today = datetime.date.today()
    d = today - relativedelta(months=1)
    d1 = datetime.date(d.year,d.month,1).strftime('%Y-%m-%d')
    d2 = (datetime.date(today.year,today.month,1) - relativedelta(days=1)).strftime('%Y-%m-%d')
    return render_template(location_page, content1=str(d1), content2=str(d2))


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


@app.route('/mapbydocfromcik', methods=['POST'])
def maobydocfromcik():
    filingorcik = str(request.form['filingorcik'])
    filingid = str(request.form['filingid'])
    doctype = str(request.form['doctype'])
    selecttype = str(request.form['selecttype'])
    return MapByDocFromCIK.run(filingorcik, filingid, doctype, selecttype)


@app.route('/searchcontentfund', methods=['POST'])
def searchcontentfund():
    processid = str(request.form['processid'])
    doctype = str(request.form['doctype'])
    return SearchContentFund.run(processid, doctype)


@app.route('/contentcompare', methods=['POST'])
def contentcompare():
    try:
        id1 = str(request.form['id1'])
        id2 = str(request.form['id2'])
        result = ContentCompare.run(id1, id2)
        return send_from_directory(directory=result[0], filename=result[1])
    except Exception as e:
        return str(e)


@app.route('/batchautomapping', methods=['POST'])
def batchautomapping():
    processid = request.form['processid']
    runqc = str(request.form['runqc'])
    mapper = str(request.form['mapper'])
    return BatchAutoMapping.run(processid, runqc, mapper, request)


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


@app.route('/namechange', methods=['POST'])
def namechange():
    processid = str(request.form['processid'])
    keywords = str(request.form['keywords'])
    return NameChange.run_result(processid, keywords)


@app.route('/batchsearthkeywords', methods=['POST'])
def batchsearchkeywords():
    ids = str(request.form['ids'])
    idtype = str(request.form['idtype'])
    keywords = str(request.form['keywords'])
    keywordtype = str(request.form['keywordtype'])
    ThreadNumber = str(request.form['ThreadNumber'])
    result = BatchSearchKeywords.run(ids, idtype, keywords, keywordtype, ThreadNumber)
    if not isinstance(result, str):
        return send_from_directory(directory=result[0], filename=result[1], as_attachment=True)
    else:
        return result


@app.route('/searchbyfundticker', methods=['POST'])
def searchbyfundticker():
    regex = str(request.form['regex'])
    processid = str(request.form['processid'])
    content = str(request.form['content'])
    if request.form.get('ignore'):
        ignore = 1
    else:
        ignore = 0
    return SearchByFundTicker.run(regex, processid, content, ignore)


@app.route('/internalauditsampling', methods=['POST'])
def internalauditsampling():
    monthdiff = int(request.form['monthdiff'])
    last_secid = str(request.form['last_secid'])
    result = InternalAuditSampling.run(monthdiff, last_secid)
    return send_from_directory(directory=common.temp_path, filename=result, as_attachment=True)


@app.route('/mappingtool', methods=['POST'])
def mappingtool():
    filingid = str(request.form['filingid'])
    return MappingTool.run(filingid)


@app.route('/timeliness', methods=['POST'])
def timeliness():
    begin_date = request.form['begindate']
    end_date = request.form['enddate']
    process = str(request.form['process'])
    resulttype = str(request.form['resulttype'])
    if request.form["action"] == 'Get Raw Data (All)':
        html_code = Timeliness.get_raw_data(begin_date, end_date, process, resulttype, data_type='All')
        if resulttype == 'HTML':
            return html_code
        else:
            return send_from_directory(directory=common.temp_path, filename=html_code, as_attachment=True)
    elif request.form["action"] ==  'Get Raw Data (>24BHr)':
        html_code = Timeliness.get_raw_data(begin_date, end_date, process, resulttype, data_type='Defect')
        if resulttype == 'HTML':
            return html_code
        else:
            return send_from_directory(directory=common.temp_path, filename=html_code, as_attachment=True)
    elif request.form["action"] == 'Get Pivot Table':
        html_code = Timeliness.get_Pivot_Table(begin_date, end_date, process)
        return html_code


@app.route('/vasubaccountcompare', methods=['POST'])
def vasubaccountcompare():
    docid = request.form['docid']
    fund_content_name_list_string = request.form['fundname']
    excel_name = VASubaccountCompare.run(docid, fund_content_name_list_string)
    return send_from_directory(directory=common.temp_path, filename=excel_name, as_attachment=True)


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
    # if len(common.domain.split(':')) > 2:
    #     port = common.domain.split(':')[2]
    # else:
    #     port = 80
    # app.run(host='0.0.0.0', port=port, threaded=True)
    app.run(host='0.0.0.0', threaded=True)