import time
start = time.perf_counter()
import js2xml
import requests
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
from itertools import repeat 
from bs4 import BeautifulSoup
from fake_headers import Headers
import pprint
import zipfile
from zipfile import ZipFile
from pathlib import Path
import google.oauth2.credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tkinter import messagebox


# Local Imports:
from Config import socialblade_cookies, socialblade_payload
from Youtube import socialblade_export

# __________Pandas Settings____________
pd.options.display.max_columns = None            
pd.options.display.max_rows = None              
pd.options.display.max_colwidth = 40            
pd.options.display.width = 2000

# _______________________________________________________ YOUTUBE CODE: GET CHANNEL NAME ____________________________________________________________

def get_channelname(url):
	youtube = build('youtube', 'v3', developerKey = socialblade_export())
	response = youtube.search().list(q = url,
									 part = 'snippet',
									 type = 'channel',
									 regionCode = 'US', 
									 maxResults = 1).execute()
									 # fields = 'items(id(kind,channelId))').execute()
	channel_name = response['items'][0]['snippet']['channelTitle']
	return channel_name.replace(" ", "").lower()


# _______________________________________________________ PREPERARTIONS ____________________________________________________________

def get_hdr():
	hdr = Headers().generate()
	return hdr


def get_url(target):
	base = 'https://socialblade.com/youtube/user/{}'
	url = base.format(str(target))
	url2 = base.format(str(target))+'/monthly'
	return url, url2


def get_request(url, url2, hdr):
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

def link_to_channel(target):
	base = 'https://www.youtube.com/{}'
	return base.format(str(target))



'''
PROBLEM
	youtube kanaler er linket på forskjellige måter: 
		https://www.youtube.com/c/          --> /c/
		https://www.youtube.com/user/       --> /user/
		https://www.youtube.com/channel/    --> /channel/ 


	Noen youtube kanaler har IKKE brukernavn i linken, og har en kode i stedet: 
		https://www.youtube.com/user/PewDiePie                      --> /PewDiePie 
		https://www.youtube.com/channel/UC8wZnXYK_CGKlBcZp-GxYPA    --> /UC8wZnXYK_CGKlBcZp-GxYPA
FIX:
	tydeligvis kan man skippe dette problemet med å fjerne mellomleddet "/user/" 
	og bare skrive brukernavnet etter ".com/". for eksempel:
		https://www.youtube.com/pewdiepie --leads-to-->  https://www.youtube.com/user/PewDiePie

	Dette funker også med kanaler uten brukernavn i URL'en: 
		https://www.youtube.com/neuralnine --leads-to--> https://www.youtube.com/channel/UC8wZnXYK_CGKlBcZp-GxYPA
	
	Det spiller heller ingen rolle om man bruker store bokstaver i brukernavnet eller ikke:
		https://www.youtube.com/NeuralNine --leads-to--> https://www.youtube.com/user/PewDiePie
		https://www.youtube.com/PEWDIEPIE  --leads-to--> https://www.youtube.com/channel/UC8wZnXYK_CGKlBcZp-GxYPA
'''


# _______________________________________________________GET USER SUMMARY____________________________________________________________
def get_user_summary(doc, rows, channel, target):
	top = get_Topinfo(doc, channel, target)
	ranks = get_ranks(rows)
	summ = get_small_stats(rows)
	return top, ranks, summ


def get_rows(doc, doc2):
	docs = [doc, doc2]
	rows_list=[]
	for i in docs:
		summary = i.find("div", id = "socialblade-user-content")
		col = summary.find_all("div")
		rows = [div.text.strip() for div in col]
		rows_list.append(rows)
	return rows_list[0], rows_list[1]


def get_Topinfo(doc, channel, target):
	Topinfo = doc.find_all("div", class_ = "YouTubeUserTopInfo")
	datalist = [['channel', target],['link to channel', channel]]
	for col in Topinfo:
		row_list = []
		for row in col:
			r = row.text.strip()
			row_list.append(r)
			row_list = list(filter(None, row_list))
		datalist.append(row_list)
	top = pd.DataFrame(datalist, columns = ['info', 'value', '_'])
	top = top.set_index(['info'])
	top = top['value']
	return top


def get_ranks(rows):
	ranks = rows[2], rows[6], rows[13], rows[20], rows[27], rows[34]
	ranks = [ i.replace(",","") for i in ranks ]
	ranks_txt = rows[3], rows[7], rows[14], rows[21], rows[28], rows[35]  
	ranks = pd.DataFrame(ranks, index = ranks_txt, columns = ['Ranks'])
	return ranks

	'''
		^^ PROBLEM ^^    Does NOT get Country-flag and Percentage ranks 
	'''

def get_small_stats(rows):
	summ = [rows[42], rows[44], rows[43], rows[50]]
	summ = [s.replace('\xa0-\xa0','') for s in summ]
	summ = [s.replace('   \n   ','') for s in summ]
	summ = [i.split('\n') for i in summ]
	titles = ([i[1] for i in summ])
	summ = [i[0].split(' ') for i in summ]
	summ = [list(filter(None, i)) for i in summ]
	summ = pd.DataFrame(summ, index=titles)
	return summ       

	'''
		^^ PROBLEM ^^    Does NOT include direction of Percentage 
	''' 




# _____________________________________________________ GET DETAILED STATISTICS ____________________________________________________________
def get_detailed_statistics(doc2, rows2):
	stats = get_table(rows2)
	avg = get_avg(rows2)
	charts = get_charts(doc2)
	return stats, charts, avg
   

def get_table(rows):
	header = rows[12] # Don't need it but nice to have if you want to print it 
	columns = ['Day','Subscriber_Change','Subscribers','Views_Change','Views','Estimated Earnings (MIN)','Estimated Earnings (MAX)']  
	table = ([x for x in rows if "\n" not in x])[17:227]      # removes all rows containing "\n"
	index = table[::7]    # Creates a new list containing every 7th list-element
	E = [i.split('\xa0\xa0-\xa0\xa0') for i in table[6::7]]
	Emin = [i[0] for i in E]
	Emax = [i[1] for i in E]
	data = table[1::7],table[2::7],table[3::7],table[4::7],table[5::7],Emin, Emax # Alternative for line 138-140:   data = table[1::7],table[2::7],table[3::7],table[4::7],table[5::7],[i[0] for i in E], [i[1] for i in E]
	stats = (pd.DataFrame(data, index=columns, columns=index)).T
	stats['Subscribers'] = stats['Subscribers'].map(lambda x: x.rstrip(' LIVE'))
	return stats

def get_avg(rows):
	avg = [x for x in rows if "\n" not in x][227:247]
	E = [i.split('\xa0-\xa0') for i in avg[4::5]]
	Emin = [i[0] for i in E]
	Emax = [i[1] for i in E]
	data = avg[2::5],  avg[3::5], Emin, Emax
	avg = (pd.DataFrame(data, columns = ['Daily Averages', 'Weekly Averages', 'Last 30 Days', 'Yearly Estimate'], index = ['Subscriber_Change', 'Views_Change','Estimated Earnings (MIN)','Estimated Earnings (MAX)'])).T
	return avg 

def get_charts(doc2):    
	script = doc2.find_all('script', type='text/javascript')
	parsed = js2xml.parse(script[7].text)
	data = [d.xpath(".//array/number/@value") for d in parsed.xpath("//property[@name='data']")]
	categories = parsed.xpath("//property[@name='categories']//string/text()")
	output =  list(zip(repeat(categories), data))
	titles = ['weekly subscribers change','weekly Video Views change',
			  
			  'total subscribers (weekly)','total Video Views (weekly)',
			  
			  'total subscribers (monthly)','total Video Views (monthly)',]
# BACKUP
	# titles før change (se change log)
		# titles = ['weekly subscribers change','weekly Video Views change', 'weekly likes change','weekly uploads change',
		# 		  'total subscribers change (weekly)','total Video Views change (weekly)', 'total likes change (weekly)','total uploads change (weekly)',	  
		# 		  'total subscribers change (monthly)','total Video Views change (monthly)', 'total likes change (monthly)','total uploads change (monthly)',]
	charts = []
	for i,title in zip(output,titles):
		data = i[1]
		date, value = data[0::2], data[1::2]
		date = [float(i) for i in date]
		df = (pd.DataFrame([date, value], index = [ 'date', title])).T
		df['date'] = pd.to_datetime(df['date'].mul(1e6).apply(pd.Timestamp)).dt.strftime('%Y-%m-%d')
		charts.append(df)
	return charts

# ______________________________________________________________________ MAIN _______________________________________________________________________
def socialblade_youtube():
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
		target = get_channelname(url)
		url, url2 = get_url(target)
		channel = link_to_channel(target) 
		hdr = get_hdr()
		try: 
			req, req2 = get_request(url, url2, hdr)	
			doc, doc2 = parse(req, req2)
			rows, rows2 = get_rows(doc,doc2)

			# Get Data
			top, ranks, summ = get_user_summary(doc, rows, channel, target)
			stats, charts, avg = get_detailed_statistics(doc2, rows2)

			# Dividing charts into groups:
			charts1 = (pd.concat(charts[:2], axis=1))
			charts2 = (pd.concat(charts[2:4], axis=1))
			charts3 = (pd.concat(charts[4:6], axis=1))

			# Print result:
			print()
			print(" -------------------------------------------------------------------- ")
			print(" |                        SOCIALBLADE / YOUTUBE                      | ")
			print(" -------------------------------------------------------------------- ")
			print()
			print()
			print("printing summ:")
			print(summ)
			print("_"*82)
			print("printing top:")
			print(top)
			print("_"*82)
			print("printing ranks:")
			print(ranks)
			print("_"*82)
			print("printing stats:")
			print(stats)
			print("_"*82)
			print("printing avg:")
			print(avg)
			print("_"*82)


			print()
			print()
			print("        ------------------------------------------------------        ")
			print("        |                 Charts Data Series                 |        ")
			print("        ------------------------------------------------------        ")
			print()
			print()

			print(f"Chart Group no.1: Gained Subscribers & Video Views Graphs for  {target} (Weekly)")
			print()
			print(charts1)
			print("_"*100)
			print(f"Chart Group no.2: Total Subscribers, & Video Views Graphs for {target} (Weekly)")
			print()
			print(charts2)        
			print("_"*100)
			print(f"Chart Group no.3: Total Subscribers, & Video Views Graphs for {target} (Monthly)")
			print()
			print(charts3)
			print("_"*100)
			
			top = top.reset_index()
			ranks = ranks.reset_index()
			summ = summ.reset_index()
			username = target
			## __________ Save All in zipfile ___________  
			path = r'output/'
			with zipfile.ZipFile(f"{path}Youtube_socialblade_data_{username}.zip", "w") as zf:
				filename =  Path(f"{username}_youtube_socialblade_top.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)

				filename =  Path(f"{username}_youtube_socialblade_ranks.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_ranks.csv", "a") as buffer:
						ranks.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_ranks.csv", "w") as buffer:
						ranks.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_youtube_youtube_socialblade_summ.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_summ.csv", "a") as buffer:
						summ.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_summ.csv", "w") as buffer:
						summ.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_youtube_socialblade_stats.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_stats.csv", "a") as buffer:
						stats.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_stats.csv", "w") as buffer:
						stats.to_csv(buffer, index = False) 


				filename =  Path(f"{username}_youtube_socialblade_avg.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_avg.csv", "a") as buffer:
						avg.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_avg.csv", "w") as buffer:
						avg.to_csv(buffer, index = False) 

				
				filename =  Path(f"{username}_youtube_socialblade_charts1.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_charts1.csv", "a") as buffer:
						charts1.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_charts1.csv", "w") as buffer:
						charts1.to_csv(buffer, index = False) 
				

				filename =  Path(f"{username}_youtube_socialblade_charts2.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_charts2.csv", "a") as buffer:
						charts2.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_charts2.csv", "w") as buffer:
						charts2.to_csv(buffer, index = False) 
			   

				filename =  Path(f"{username}_youtube_socialblade_charts3.csv")
				if filename.exists():
					with zf.open(f"{username}_youtube_socialblade_charts3.csv", "a") as buffer:
						charts3.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_youtube_socialblade_charts3.csv", "w") as buffer:
						charts3.to_csv(buffer, index = False)
			print()   
			print(f"    file saved as: Youtube_socialblade_data_{username}.zip, in: {path}")
			print("    "+"_" * 100)


		except: 
			print(f"	ERROR: {target} does not have a Socialblade Profile")
			print()
		print()
		print("exit: Socialblade Scraper")

if __name__ == '__main__':
	socialblade_youtube()
	finish = time.perf_counter()
	print(f'Finished in {round(finish - start, 2)} second(s)')
	messagebox.showinfo("Notification", "Socialblade scraping is complete.")
