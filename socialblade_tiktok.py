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
from tkinter import messagebox
from tkinter import messagebox


# Local Imports:
from Config import socialblade_cookies, socialblade_payload

# __________Pandas Settings____________
pd.options.display.max_columns = None            
pd.options.display.max_rows = None
pd.options.display.max_colwidth = 40
pd.options.display.width = 2000  



# _______________________________________________________ PREPERARTIONS ____________________________________________________________
def get_hdr():
	hdr = Headers().generate()
	return hdr

def get_url(target):
	base = 'https://socialblade.com/tiktok/user/{}'
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

def get_username(url):
	username = url.split('/')[3]
	return username

# _______________________________________________________GET USER SUMMARY____________________________________________________________

def get_user_summary(doc, rows):
	top = get_Topinfo(doc)
	ranks = get_ranks(rows)
	summ = get_small_stats(doc)
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
	top = pd.DataFrame(datalist[1], index = datalist[0], columns = ['Current Stats'])
	# top = top.set_index(['info'])
	top = top[0:4]
	return top


def get_ranks(rows):
	ranks = str(rows[0]).split("\n\n")  
	ranks = [i for i in ranks if i]
	ranks = [s.strip('\n        ') for s in ranks]
	index, ranks = ranks[1::2], ranks[::2]
	ranks = pd.DataFrame(ranks, index = index, columns=["Ranking"])
	return ranks


def get_small_stats(doc):
	summary = doc.find("div", id = "socialblade-user-content")
	col = summary.find_all("div")
	rows = []
	for div in col:
		r = div.text.strip()
		rows.append(r)
	summ = rows[16], rows[17], rows[18]
	summ = [i.split('\n') for i in summ]
	titles = ([i[1] for i in summ])
	summ = [i[0].split(' ') for i in summ]
	summ = [list(filter(None, i)) for i in summ]
	summ = pd.DataFrame(summ, index=titles, columns=['Value', '%Change'])
	return summ       

	'''
		^^ PROBLEM ^^    Does NOT include direction of Percentage 
	''' 




# _____________________________________________________ GET DETAILED STATISTICS ____________________________________________________________
def get_detailed_statistics(doc2, rows2, target):
	stats = get_table(rows2)
	avg = get_avg(rows2)
	charts = get_charts(doc2, target)
	return stats, charts, avg

   
def get_table(rows2):
	header = rows2[11] #Don't need it but nice to have if you want to print it 
	columns = ['Day', 'Follower_change', 'Followers', 'Following_change', 'Following', 'Likes_change', 'Likes', 'Upload_change', 'Uploads']
	data = str(rows2[18]).split("\n")
	data = [s.strip('                            ') for s in data]
	data = list(filter(None, data))
	stats = (pd.DataFrame([ data[1::10], data[2::10], data[3::10], 
							data[4::10], data[5::10], data[6::10], 
							data[7::10], data[8::10], data[9::10]], 
							index = columns, columns = data[0::10])).T
	stats.index.names = ['Date']
	return stats



def get_avg(rows2):
	index = ["Daily Averages", "Last 30 Days"]
	columns = ['gained followers', 'gained likes', 'change avg uploads']
	values = [[rows2[505], rows2[507], rows2[508]], [rows2[511], rows2[513], rows2[514]]]
	avg = pd.DataFrame(values, index = index, columns=columns) 
	return avg 


def get_charts(doc2):    
	script = doc2.find_all('script', type = 'text/javascript')

	parsed = js2xml.parse(script[7].text)
	data = [d.xpath(".//array/number/@value") for d in parsed.xpath("//property[@name='data']")]
	categories = parsed.xpath("//property[@name='categories']//string/text()")
	output =  list(zip(repeat(categories), data))

	titles = ['weekly followers change','weekly following change', 'weekly likes change','weekly uploads change',
			  'total followers change (weekly)','total following change (weekly)', 'total likes change (weekly)','total uploads change (weekly)',
			  'total followers change (monthly)','total following change (monthly)', 'total likes change (monthly)','total uploads change (monthly)',]
	charts = []
	for i, title in zip(output,titles):
		data = i[1]
		date, value = data[0::2], data[1::2]
		date = [float(i) for i in date]
		df = (pd.DataFrame([date, value], index = ['date', title])).T
		df['date'] = pd.to_datetime(df['date'].mul(1e6).apply(pd.Timestamp)).dt.strftime('%Y-%m-%d')
		charts.append(df)
	return charts

# TEST get_charts(doc2):
		# def chart_df(date, value, data, title): # Belongs to "charts=" [line 191]
		#     # date_new = chart_float(date)
		#     # date = [float(i) for i in date]
		#     df = (pd.DataFrame([date_new, value], index = [ 'date', title])).T
		#     df['date'] = pd.to_datetime(df['date'].mul(1e6).apply(pd.Timestamp)).dt.strftime('%Y-%m-%d')
		#     return df         

		# def chart_float(date_list):                  # Belongs to "charts=" [line 191]
		#     return [float(d) for d in date_list]

		# date = [chart_float(data[0::2]) for i, title in zip(output,titles)] 
		# charts = [(chart_df(date, data[1::2], i[1], title)) for i, title in zip(output,titles)] for i in date   # Controlls --> chart_df [line 182]  &  chart_float [line 188]           
		# charts = [(chart_df(data[0::2], data[1::2], i[1], title)) for i, title in zip(output,titles)]   # Controlls --> chart_df [line 182]  &  chart_float [line 188]           
		# return charts

# get_charts(doc2) KOPIERT FRA SOCIALBLADE_INSTAGRAM
def get_charts(doc2, target):    
	script = doc2.find_all('script', type='text/javascript')
	parsed = js2xml.parse(script[7].text)
	data = [d.xpath(".//array/number/@value") for d in parsed.xpath("//property[@name='data']")]
	categories = parsed.xpath("//property[@name='categories']//string/text()")
	output =  list(zip(repeat(categories), data))
	titles = [f'{target}: Tiktok,  weekly followers change', f'{target}: Tiktok, weekly following change', f'{target}: Tiktok, weekly likes change', f'{target}: Tiktok, weekly uploads change', 

			  f'{target}: Tiktok, total followers change (weekly)', f'{target}: Tiktok, total following change (weekly)', f'{target}: Tiktok, total likes change (weekly)', f'{target}: Tiktok, total uploads change (weekly)',
			 
			  f'{target}: Tiktok, total followers change (monthly)', f'{target}: Tiktok, total following change (monthly)', f'{target}: Tiktok, total likes change (monthly)', f'{target}: Tiktok, total uploads change (monthly)',]
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
def socialblade_tiktok():
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
		hdr = get_hdr()
		try:
			req, req2 = get_request(url, url2, hdr)
			doc, doc2 = parse(req, req2)
			rows, rows2 = get_rows(doc,doc2)

			#Get User Summary:
			top, ranks, summ = get_user_summary(doc, rows)

			#Get detailed Stats:
			stats, charts, avg = get_detailed_statistics(doc2, rows2, target)

			# Dividing charts into groups:
			charts1 = (pd.concat(charts[:4], axis=1))#.set_index('date')
			charts2 = (pd.concat(charts[4:8], axis=1))#.set_index('date')
			charts3 = (pd.concat(charts[9:12], axis=1))#.set_index('date')

			# Print result:
			print()
			print(" -------------------------------------------------------------------- ")
			print(" |                        SOCIALBLADE / TIKTOK                      | ")
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

			top=top.reset_index()
			ranks=ranks.reset_index()
			summ=summ.reset_index()
			username=target
			## __________ Save All in zipfile ___________ 
			path=r'output/'
			with zipfile.ZipFile(f"{path}TikTok_socialblade_data_{username}.zip", "w") as zf:
				filename =  Path(f"{username}_tiktok_socialblade_top.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_top.csv", "w") as buffer:
						top.to_csv(buffer, index = False)

				filename =  Path(f"{username}_tiktok_socialblade_ranks.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_ranks.csv", "a") as buffer:
						ranks.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_ranks.csv", "w") as buffer:
						ranks.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_tiktok_socialblade_summ.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_summ.csv", "a") as buffer:
						summ.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_summ.csv", "w") as buffer:
						summ.to_csv(buffer, index = False) 

				filename =  Path(f"{username}_tiktok_socialblade_stats.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_stats.csv", "a") as buffer:
						stats.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_stats.csv", "w") as buffer:
						stats.to_csv(buffer, index = False) 


				filename =  Path(f"{username}_tiktok_socialblade_avg.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_avg.csv", "a") as buffer:
						avg.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_avg.csv", "w") as buffer:
						avg.to_csv(buffer, index = False) 

				
				filename =  Path(f"{username}_tiktok_socialblade_charts1.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_charts1.csv", "a") as buffer:
						charts1.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_charts1.csv", "w") as buffer:
						charts1.to_csv(buffer, index = False) 
				

				filename =  Path(f"{username}_tiktok_socialblade_charts2.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_charts2.csv", "a") as buffer:
						charts2.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_charts2.csv", "w") as buffer:
						charts2.to_csv(buffer, index = False) 
			   

				filename =  Path(f"{username}_tiktok_socialblade_charts3.csv")
				if filename.exists():
					with zf.open(f"{username}_tiktok_socialblade_charts3.csv", "a") as buffer:
						charts3.to_csv(buffer, index = False)
				else:
					with zf.open(f"{username}_tiktok_socialblade_charts3.csv", "w") as buffer:
						charts3.to_csv(buffer, index = False) 
			# print(f"Data has been saved as:  {path}_Tiktok_socialblade_data_{username}.zip")
			print()   
			print(f"    file saved as: Tiktok_socialblade_data_{username}.zip, in: {path}")
			print("    "+"_" * 100)


		except: 
			print(f"	ERROR: {target} does not have a Socialblade Profile")
			print()
		print()
		print("exit: Socialblade Scraper")


if __name__ == '__main__':
	
	socialblade_tiktok()
	print(f'Finished in {round(((time.perf_counter()-start)+0.12),2)} second(s)')
	messagebox.showinfo("Notification", "Socialblade scraping is complete.")
