#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
#------------------------------------
#--Author:        Jeffrey Yu
#--CreationDate:  2017/10/24 14:00
#--RevisedDate:   
#------------------------------------

import os
import pandas as pd
import datetime
import common


def rename(x, type='umbrella'):
	if type == 'umbrella':
		dicts = Umbrella_dict
	elif type == 'fund1':
		dicts = Fund_dict_Abbr_1
	elif type == 'fund2':
		dicts = Fund_dict_Abbr_2
	elif type == 'specialword':
		dicts = Special_words
	elif type == 'others':
		dicts = Others
	for each_word in dicts.keys():
		if each_word in x:
			x = x.replace(each_word, dicts[each_word])
			if (type == 'fund1' or type == 'fund2') and len(x) <= 40:
				return x
	return x


def replace_word_1(x):
	if x in Fund_dict_Abbr_1.keys():
		x = Fund_dict_Abbr_1[x]
	return x


def reverse_list(x):
	i = len(x)
	new_x = []
	while i > 0:
		i = i - 1
		new_x.append(x[i])
	return new_x


def remove_blank(x, blank_type=0):
	if ',' in x:
		x = x.replace(',',', ')
	if '.' in x:
		x = x.replace('.','. ')
	x = ' '.join(filter(lambda x: x, x.split(' ')))
	if blank_type != 0:
		x += ' '
	return x


def capitalize_word(x):
	x = ' '.join(word[0].upper() + word[1:] for word in x.split())
	return x


def remove_head(x):
	if x[0] == '-':
		x = x[1:]
	if x[1] == '-':
		x = x[2:]
	if x[2] == '-':
		x = x[3:]
	if x[0] == ' ':
		x = x[1:]
	return x


Umbrella_dict = {}
with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Umbrella_dict.txt', 'r', encoding='UTF-8') as r_d:
	for line in r_d.readlines():
		list1 = line.split('#')
		a = str(list1[0].strip('\n'))
		b = str(list1[1].strip('\n'))
		Umbrella_dict[a] = b

Fund_dict_Abbr_1 = {}
with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Fund_dict_Abbr_1.txt', 'r', encoding='UTF-8') as r_d:
	if r_d.read() == '':
		Fund_dict_Abbr_1 = {"":""}
	else:
		with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Fund_dict_Abbr_1.txt', 'r', encoding='UTF-8') as r_d:
			for line in r_d.readlines():
				list1 = line.split('#')
				a = str(list1[0].strip('\n'))
				b = str(list1[1].strip('\n'))
				Fund_dict_Abbr_1[a] = b

Fund_dict_Abbr_2 = {}
with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Fund_dict_Abbr_2.txt', 'r', encoding='UTF-8') as r_d:
	if r_d.read() == '':
		Fund_dict_Abbr_2 = {"":""}
	else:
		with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Fund_dict_Abbr_2.txt', 'r', encoding='UTF-8') as r_d:
			for line in r_d.readlines():
				list1 = line.split('#')
				a = str(list1[0].strip('\n'))
				b = str(list1[1].strip('\n'))
				Fund_dict_Abbr_2[a] = b

Special_words = {}
with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Special_words.txt', 'r', encoding='UTF-8') as r_d:
	for line in r_d.readlines():
		list1 = line.split('#')
		a = str(list1[0].strip('\n'))
		b = str(list1[1].strip('\n'))
		Special_words[a] = b

Others = {}
with open(common.cur_file_dir() + '\\static\\Rename_Tool_dicts\\Others.txt', 'r', encoding='UTF-8') as r_d:
	for line in r_d.readlines():
		list1 = line.split('#')
		a = str(list1[0].strip('\n'))
		b = str(list1[1].strip('\n'))
		Others[a] = b


def run(x):

	fundlist = []
	xx = x.split('\n')
	for fundname in xx:
		fundname = str(fundname.strip('\n'))
		fundname = str(fundname.strip('\r'))
		fundlist.append(fundname)

	result_file = 'Rename_Result-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.csv'
	result_file_path = common.temp_path

	all_fund = []
	for fund in fundlist:
		fund_detail = []
		old_name = fund
		# fund = capitalize_word(remove_blank(fund, blank_type=0))
		if ' - ' in fund:
			symbol_location = fund.find(' - ') + 1
			before_fund = remove_blank(fund[0:symbol_location], blank_type=0)
			after_fund = remove_blank(capitalize_word(fund[symbol_location + 1:]), blank_type=0)

			before_fund = rename(before_fund, type='specialword')
			before_fund = rename(before_fund, type='umbrella')

			after_fund = rename(after_fund, type='specialword')
			after_fund = rename(after_fund, type='fund1')
			after_word_list = after_fund.split(' ')
			new_after_fund_list = []
			for each_word in reverse_list(after_word_list):
				each_word = replace_word_1(each_word)
				new_after_fund_list.append(each_word)
			after_fund = ' '.join(reverse_list(new_after_fund_list))
			after_fund = rename(after_fund, type='others')
			after_fund = rename(after_fund, type='fund1')

			fund = before_fund + ' - ' + after_fund
			fund = remove_blank(fund, blank_type=0)

			if len(fund) > 40:
				fund = rename(fund, type='fund1')
				fund = remove_blank(fund, blank_type=0)
				if len(fund) > 40:
					fund = rename(fund, type='fund2')
			fund = fund.replace(' - ',' ')
		else:
			fund = rename(fund, type='specialword')
			fund = rename(fund, type='others')
			fund = rename(fund, type='fund1')
			fund_list = fund.split(' ')
			new_fund_list = []
			for each_word in reverse_list(fund_list):
				each_word = replace_word_1(each_word)
				new_fund_list.append(each_word)
			fund = ' '.join(reverse_list(new_fund_list))
			fund = rename(fund, type='fund1')
			fund = remove_blank(fund,blank_type=0)
			if len(fund) > 40:
				fund = rename(fund, type='fund2')

		fund = remove_blank(remove_head(fund), blank_type=0)
		new_name = fund
		name_num = len(new_name)
		fund_detail = [old_name, new_name, name_num]
		all_fund.append(fund_detail)

	df = pd.DataFrame(all_fund, columns=['Old Name', 'New Name', 'New Name Length'])

	try:
		if os.path.isfile(result_file_path + result_file):
			os.remove(result_file_path + result_file)
		df.to_csv(result_file_path + result_file, encoding='GB18030')
	except:
		if os.path.isfile(result_file_path + result_file):
			os.remove(result_file_path + result_file)
		df.to_csv(result_file_path + result_file, encoding='UTF-8')

	return result_file


