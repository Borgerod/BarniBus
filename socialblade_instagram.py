import time
start = time.perf_counter()
import smtplib, ssl
import requests
from bs4 import BeautifulSoup
import time
from fake_headers import Headers
import pandas as pd
import numpy as np
import ast
import json
import re
import js2xml
from itertools import repeat   
from pprint import pprint
import datetime as dt
from datetime import datetime
from lxml.etree import tostring
import pprint

import cfscrape
import pprint
import json
from bs4 import BeautifulSoup, Comment
import zipfile
from zipfile import ZipFile
from pathlib import Path
from tkinter import messagebox

# TEST imports
from html.parser import HTMLParser
import html
import re

# Local Imports:
from Config import socialblade_cookies, socialblade_payload

# __________Pandas Settings____________
pd.options.display.max_columns = None            
pd.options.display.max_rows= None              
pd.options.display.max_colwidth = 40            
pd.options.display.width = 2000


# _____________________________________________ PREPERARTIONS ____________________________________________________________
def get_username(url):
	username = url.split('/')[3]
	return username

def get_hdr():
	hdr = Headers().generate()
	return hdr


def get_url(target):
	base = 'https://socialblade.com/instagram/user/{}'
	url = base.format(str(target))
	url2 = base.format(str(target))+'/monthly'
	return url, url2

def get_request(url, url2, hdr, payload):
	while True:
		with requests.Session() as s:
			p = s.post(url, data = socialblade_payload)
			req = s.get(url, cookies = socialblade_cookies, headers = hdr)
			req2 = s.get(url2, cookies = socialblade_cookies, headers = hdr)
			return req, req2

def parse(req, req2):
	doc = BeautifulSoup(req.content, 'lxml')
	doc2 = BeautifulSoup(req2.content, 'lxml')
	return doc, doc2


# _____________________________________________GET USER SUMMARY____________________________________________________________
def get_user_summary(doc, rows):
	top = get_Topinfo(doc)
	ranks = get_ranks(rows)
	summ = get_small_stats(doc)
	return top, ranks, summ


def get_rows(doc, doc2):
	docs = [doc, doc2]
	rows_list = []
	for i in docs:
		summary = i.find("div", id = "socialblade-user-content")
		col = summary.find_all("div")
		rows = [div.text.strip() for div in col]
		rows_list.append(rows)
	return rows_list[0], rows_list[1]


def get_Topinfo(doc):
	Topinfo = doc.find_all("div", class_ = "YouTubeUserTopInfo")
	datalist = []
	for col in Topinfo:
		row_list = []
		for row in col:
			r = row.text.strip()
			row_list.append(r)
			row_list = list(filter(None, row_list))
		datalist.append(row_list)
	top = pd.DataFrame(datalist, columns = ['info', 'value'])
	top = top.set_index(['info'])
	top = top['value']
	return top


def get_ranks(rows):
	ranks = rows[2],rows[6],rows[9],rows[12],rows[15]
	ranks = [ i.replace(",","") for i in ranks ]
	ranks_txt = rows[3],rows[7],rows[10],rows[13],rows[16] 
	ranks = pd.DataFrame(ranks, index = ranks_txt, columns = ['Ranks'])
	return ranks

def get_small_stats(doc): 
	summary = doc.find("div", id = "socialblade-user-content")
	summary = [i for i in summary]
	summary = summary[::2]
	summ = summary[2]
	summ = (list(summ))[1::2]
	summ = [str(i).split('</p>', 1)[0] for i in summ]
	result = [(re.search('\r\n        (.*)<sup', s)).group(1) for s in summ]
	summ = pd.DataFrame(result, index = ['Followers for the last 30 days', 'Following for the last 30 days', 'Media for the last 30 days'], columns=['Last30d'])
	return summ

	'''
		^^ PROBLEM ^^    Does NOT include direction of Percentage 
	''' 




# _____________________________________________GET DETAILED STATISTICS____________________________________________________________
def get_detailed_statistics(doc2, rows2):
	stats = get_table(rows2)
	avg = get_avg(rows2)
	charts = get_charts(doc2)
	return stats, charts, avg


def get_table(rows):
	table = ([x for x in rows if "\n" not in x][10:256])[1:] 
	table = table[5:]
	rows = [table[x:x+8] for x in range(0, len(table),8)]
	stats = pd.DataFrame(rows, columns=['Day','day_of_week','follower_Change','followers','following_change','following','media_uploads','total_media_uploads'])
	return stats


def get_avg(rows):
	avg = [x for x in rows if "\n" not in x][260:267]
	rows = [avg[x:x+3] for x in range(0, len(avg),4)]
	avg = pd.DataFrame(rows, index=['Daily Average', 'Last 30 Days'], columns=['change_followers', 'change_following', 'change_uploads'])
	return avg
 

def get_charts(doc2):    
	script = doc2.find_all('script', type='text/javascript')
	parsed = js2xml.parse(script[7].text)
	data = [d.xpath(".//array/number/@value") for d in parsed.xpath("//property[@name='data']")]
	categories = parsed.xpath("//property[@name='categories']//string/text()")
	output =  list(zip(repeat(categories), data))
	titles = ['weekly followers change','weekly following change','weekly uploads change',

			  'total followers (weekly)', 'total following (weekly)', 'total uploads (weekly)',

			  'total followers (monthly)','total following (monthly)','total uploads (monthly)',]
# BACKUP 
	# titles før change (se change log)
		# titles = ['weekly followers change','weekly following change', 'weekly likes change','weekly uploads change',
			  # 'total followers change (weekly)','total following change (weekly)', 'total likes change (weekly)','total uploads change (weekly)',
			  # 'total followers change (monthly)','total following change (monthly)', 'total likes change (monthly)','total uploads change (monthly)',]
	charts = []
	for i,title in zip(output,titles):
		data = i[1]
		date = data[0::2]
		value = data[1::2]
		date = [float(i) for i in date]
		df = (pd.DataFrame([date, value], index = [ 'date', title])).T
		df['date'] = pd.to_datetime(df['date'].mul(1e6).apply(pd.Timestamp)).dt.strftime('%Y-%m-%d')
		charts.append(df)
	return charts


# ______________________________________________________________________ MAIN _______________________________________________________________________
def socialblade_instagram():
	print("=" * 100)
	print()
	print("initiate: Socialblade Scraper")
	print()
	print("    "+"_" * 80)	
	urls = []
	with open("url_list.txt","r") as file:
		for line in file:
			urls.extend(line.split())
	for url in urls:
		target = get_username(url)
		url, url2 = get_url(target)
		hdr=get_hdr()
		try: 
			req, req2 = get_request(url, url2, hdr, payload)
			doc, doc2 = parse(req, req2)
			rows, rows2 = get_rows(doc,doc2)
			
			# get data
			top, ranks, summ = get_user_summary(doc, rows)
			stats, charts, avg = get_detailed_statistics(doc2, rows2)

			# Dividing charts into groups:
			charts1 = (pd.concat(charts[:3], axis=1))#.set_index('date')
			charts2 = (pd.concat(charts[3:6], axis=1))#.set_index('date')
			charts3 = (pd.concat(charts[6:10], axis=1))#.set_index('date')
			#drop date columns
			charts1 = (charts1.set_index(charts1.iloc[:, 0])).drop('date',axis=1)
			charts2 = (charts2.set_index(charts2.iloc[:, 0])).drop('date',axis=1)
			charts3 = (charts3.set_index(charts3.iloc[:, 0])).drop('date',axis=1)
			# #reset index
			charts1 = charts1.reset_index()
			charts2 = charts2.reset_index()
			charts3 = charts3.reset_index()

			# Print result:
			print()
			print(" -------------------------------------------------------------------- ")
			print(" |                     SOCIALBLADE / INSTAGRAM                      | ")
			print(" -------------------------------------------------------------------- ")
			print()
			print()
			print(summ)
			print("_"*82)
			print(top)
			print("_"*82)
			print(ranks)
			print("_"*82)
			print(stats)
			print("_"*82)
			print(avg)
			print("_"*82)
			print()
			print()
			print("        ------------------------------------------------------        ")
			print("        |                 Charts Data Series                 |        ")
			print("        ------------------------------------------------------        ")
			print()
			print()
			print(f"Chart Group no.1: Change in Followers, Following, & uploads Graphs for {target} (Weekly)")
			print()
			print(charts1)
			print("_"*100)
			print(f"Chart Group no.1: Total Followers, Following, & uploads Graphs for {target} (Weekly)")
			print()
			print(charts2)        
			print("_"*100)
			print(f"Chart Group no.1: Total Followers, Following, & uploads Graphs for {target} (Monthly)")
			print()
			print(charts3)
			print("_"*100)


			top = top.reset_index()
			ranks = ranks.reset_index()
			summ = summ.reset_index()
			username = target

			## __________ Save All in zipfile ___________  
			path = r'output/'
			with zipfile.ZipFile(f"{path}Instagram_socialblade_data_{username}.zip", "w") as zf:
				filename =  Path(f"{username}_instagram_socialblade_top.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)

				filename =  Path(f"{username}_instagram_socialblade_ranks.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_ranks.csv", "a") as buffer:
						ranks.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_ranks.csv", "w") as buffer:
						ranks.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_instagram_socialblade_summ.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_summ.csv", "a") as buffer:
						summ.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_summ.csv", "w") as buffer:
						summ.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_instagram_socialblade_stats.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_stats.csv", "a") as buffer:
						stats.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_stats.csv", "w") as buffer:
						stats.to_csv(buffer, index = False) 


				filename =  Path(f"{username}_instagram_socialblade_avg.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_avg.csv", "a") as buffer:
						avg.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_avg.csv", "w") as buffer:
						avg.to_csv(buffer, index = False) 

				
				filename =  Path(f"{username}_instagram_socialblade_charts1.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_charts1.csv", "a") as buffer:
						charts1.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_charts1.csv", "w") as buffer:
						charts1.to_csv(buffer, index = False) 
				

				filename =  Path(f"{username}_instagram_socialblade_charts2.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_charts2.csv", "a") as buffer:
						charts2.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_charts2.csv", "w") as buffer:
						charts2.to_csv(buffer, index = False) 
			   

				filename =  Path(f"{username}_instagram_socialblade_charts3.csv")
				if filename.exists():
					with zf.open(f"{username}_instagram_socialblade_charts3.csv", "a") as buffer:
						charts3.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_instagram_socialblade_charts3.csv", "w") as buffer:
						charts3.to_csv(buffer, index = False)
			print()   
			print(f"    file saved as: Instagram_socialblade_data_{username}.zip, in: {path}")
			print("    "+"_" * 100)


		except: 
			print(f"	ERROR: {target} does not have a Socialblade Profile")
			print()
		print()
		print("exit: Socialblade Scraper")


if __name__ == '__main__':
	socialblade_instagram()
	print(f'Finished in {round(((time.perf_counter()-start)+0.12),2)} second(s)')
	messagebox.showinfo("Notification", "Socialblade scraping is complete.")






# _____________________ OLD CODE______________________
# def get_last30(rows):
	# last30 = rows[15]
	# last30 = str(last30).split("\n")
	# # last30 = str(last30).split("\n\n")
	# last30 = [i for i in last30 if i]
	# last30 = [s.strip('\n        ') for s in last30]
	# last30 = [s.replace('M','000000') for s in last30]
	# last30 = [s.replace('.','') for s in last30]
	# index, last30 = last30[1::2], last30[::2]
	# change = [i.split(' ')[1] for i in last30]
	# last30 = [i.split(' ')[0] for i in last30]
	# last30 = pd.DataFrame([last30, change],columns = index)
	# return last30