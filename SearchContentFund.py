#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/12/12 13:52
#--RevisedDate:   
#------------------------------------

import re
import difflib
import pyodbc
import pandas as pd
import File_OP as fo
import common


def compare_ratio(a, b):
	dff = difflib.SequenceMatcher(None, a, b)
	dff_ratio = dff.ratio()
	return dff_ratio


def run(id, SupplementDocType):
	try:
		# By doc from CIK
		connection = pyodbc.connect(common.connection_string_multithread)
		code1 = '''
			select Comment as a
				from DocumentAcquisition..MasterProcess as mp
				where Comment is not null
				and Category=1
				and Status<>5
				and mp.ProcessId=%s
		''' % id
		cursor = connection.cursor()
		result1 = cursor.execute(code1).fetchall()

		if len(result1) > 0:
			a = result1[0][0]
			b = a[9:len(a) - 1]
			filingid = b
		else:
			code2 = '''
				select distinct fsc.FilingId
				from DocumentAcquisition..FilingSECContract as fsc
				left join DocumentAcquisition..MasterProcess as mp on fsc.FilingId=mp.ContainerId
				where mp.ProcessId=%s
			''' % id
			result2 = cursor.execute(code2).fetchall()
			filingid = result2[0][0]
		code = '''
			Declare
			@SupplementDocType int
			Set @SupplementDocType=%s
			select distinct fb.LegalName
			--CONVERT(varchar(10),mp.EffectiveDate,120) as [EffectiveDate]
			from
			(select A.FilingId,A.CIK ,ii.InvestmentId
			from
			(
			select distinct fsc.FilingId,fsc.CIK
			from DocumentAcquisition..FilingSECContract as fsc
			where fsc.FilingId in(%s)
			) as A
			left join DocumentAcquisition..FilingSECContract as fsc2 on fsc2.CIK=A.CIK
			left join CurrentData..InvestmentIdentifier as ii on ii.Identifier=fsc2.ContractId and ii.IdentifierType=20
			left join SecurityData..SecuritySearch as ss on ss.SecId=ii.InvestmentId
			where ss.Status<>0) as B
			left join DocumentAcquisition..SECCurrentDocument as scd on scd.InvestmentId=B.InvestmentId
			left join DocumentAcquisition..MasterProcess as mp on mp.DocumentId=scd.DocumentId
			left join DocumentAcquisition..SECFiling as sf on sf.FilingId=mp.ContainerId
			left join DocumentAcquisition..InvestmentMapping as im on im.ProcessId=mp.ProcessId
			left join SecurityData..SecuritySearch as SS on SS.SecId=im.InvestmentId
			left join [CurrentData].[dbo].[FundBasic]as fb on fb.FundId=SS.FundId ---找到Legalname
			left join DocumentAcquisition..SystemParameter as sp on sp.CodeInt=mp.DocumentType and sp.CategoryId=105
			where mp.DocumentType=case when @SupplementDocType=2  then 1--supplement=2
									   when @SupplementDocType=15 then 3-----supplement to SAI=15
									   when @SupplementDocType=60 then 17-----Sup to Summary Prospectus=60
									   end

			and SS.Status<>0
			group by
			fb.LegalName
			order by fb.LegalName
		''' % (SupplementDocType, filingid)
		cursor = connection.cursor()
		result = cursor.execute(code).fetchall()
		LegalName = []
		for item in result:
			LegalName.append(item[0].title())

		# Extract Content Fund
		Doctext = fo.get_doc_conent(id, idtype='ProcessId', source='DAP', method=1)
		reglex = re.compile('\\s(?:[0-9A-Z&][^,\\"@\\s\\n\\r\\t]*?\\s{1,2}){1,10}?(?:Fund|ETF|Portfolio|Reserves|RESERVES|FUND|PORTFOLIO|VP|VIP)\\b')
		Funds = re.findall(reglex,Doctext)
		# 去重
		Funds = list(set(Funds))

		with open(common.cur_file_dir() + '\\static\\SearchContentFund\\invalid_fund.txt', 'r') as e:
			msgs = e.read()
			invalid = msgs.split(',')
		Filter_Funds = [Fund.title().strip() for Fund in Funds if Fund not in invalid]

		# 根据匹配度进行排序
		test = []
		while len(Filter_Funds) != 0 and len(LegalName) != 0:
			temps = []
			for a in Filter_Funds:
				for b in LegalName:
					ratio = compare_ratio(a, b)
					lst = [a, b, ratio]
					temps.append(lst)
			temps.sort(key=lambda temp:temp[2], reverse=True)
			test.append(temps[0])
			LegalName.remove(temps[0][1])
			Filter_Funds.remove(temps[0][0])
		No_match = [row1 for row1 in LegalName if row1 not in [row[1] for row in test ]]
		No_match_fundlist = [['', row, 0] for row in No_match]
		final_result = test+No_match_fundlist

		# 输出html结果
		a = pd.DataFrame.from_records(data=final_result, columns=['ContentFund', 'LegalName', 'Diff Ratio']).sort_values(by='Diff Ratio', ascending=False)
		pd.set_option('display.max_colwidth', -1)
		html_code = a.to_html(classes='tablestyle',index=False)
		html_code = common.css_code + html_code
		return html_code
	except Exception as e:
		return 'Error: ' + str(e)

