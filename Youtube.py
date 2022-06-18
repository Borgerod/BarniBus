'''
________TO-DO_________
	"[X] means done"

	1.  [ ] 
	2.  [ ] 
	3.  [ ] Clean up imports 
	4.  [ ] Create URL Loop
	5.  [ ] Create API Loop
	6.  [ ] Fill Youtube Requirements
		YOUTUBE CHANNEL REQUIREMENTS:
		1.  [X] Username
		2.  [X] Link
		3.  [X] subs
		4.  [X] uploads
		5.  [X] Verified
		6.  [X] bio length
		7.  [X] 3 dominant colours of profile pic
		8.  [X] Daily Averge Uploads (based on last 60days)

		YOUTUBE VIDEO REQUIREMENTS:
		1.  [X] A link to the post
		2.  [X] Number of views
		3.  [X] Number of likes
		4.  [X] Number of comments
		5.  [X] The views/followers %
		6.  [X] Number of characters in the post caption.
		7.  [X] The number of tags in the post. (Might need to use an app like VidIq to check this.)

		If possible, also add the data of the thumbnail:
		7.  [ ] [UNLIKELY] How many characters (letters, numbers, etc.) are in the thumbnail, if any.    
		8.  [ ] [UNLIKELY] The color of the text
		9.  [X] [DOABLE] The dominant 5 colors of the thumbnail in the 5 separate cells as the hex code
		10. [ ] [MAYBE] How many faces are on the thumbnail, if any. (Again if possible to scan)
[       Open Me       ]
_______________________
'''

'''
________BUGS__________
	"[X] means bug is fixed"

	1.  [X] "Nextpage Token-bug"    (see: Benjamin_full_response.py)
	2.  [ ] "Description-bug"       (descr: Does not fetch full video-description)
	3.  [ ] "All_Videos-bug"        (descr: Does not fetch all vids, skips first and last)
	4.  [X] "tags-bug"              (see: Benjamin_Tags_bug.py)
	5.  [ ] "Chunk-bug"             (descr: Still creates chunks when id_list<50, see: Benjamin_Tags_bug.py)
	6.  [ ] "upload_rate-bug"       (descr: Uploads rate wouldn't show, printed out a function)
	7.  [ ] "id_list"               (descr: id_list is not defined at line 221)
[       Open Me       ]
_______________________

'''

#____Count the time____
import time
start = time.perf_counter()

#____Regular imports____
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import pandas as pd
import os
import csv

import google.oauth2.credentials
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.api_core.exceptions import AlreadyExists, NotFound
from googleapiclient.discovery import build
import argparse

from emoji import UNICODE_EMOJI
from fake_headers import Headers
from bs4 import BeautifulSoup
import requests

import pprint
import json
import datetime as dt
from datetime import date
from datetime import timedelta
import re

import pandas as pd
import zipfile
from zipfile import ZipFile
from pathlib import Path
import pandas as pd
import argparse
from tkinter import messagebox

# __________ Local Imports ____________
from api_keys import youtube_keys
from Color_counter import top_colors, top_colors_profile_pic



# __________Pandas Settings____________
pd.options.display.max_columns = None            
pd.options.display.max_rows = None              
pd.options.display.max_colwidth = None            
pd.options.display.width = 2000


# __________________________________________________________________ CHANNEL ID ____________________________________________________________________
def get_channelId(youtube, url):
	response = youtube.search().list(q = url,
									 part = 'snippet',
									 type = 'channel',
									 regionCode = 'US', 
									 maxResults = 1).execute()
									 # fields = 'items(id(kind,channelId))').execute()

	channelId = response['items'][0]['id']['channelId']
	# print(channelId)
	return channelId


# __________________________________________________________________ CHANNEL INFO __________________________________________________________________
def get_channel_info(youtube, channelId):
	response = youtube.channels().list(part = 'id, snippet, statistics',
									   id = channelId).execute()

	verf                =  check_verification(channelId)
	channel_link        =  f"https://www.youtube.com/channel/{channelId}"
	title               =  response['items'][0]['snippet']['title']
	profile_picture     =  response['items'][0]['snippet']['thumbnails']['high']['url']
	tot_views           =  response['items'][0]['statistics']['viewCount']
	tot_subs            =  response['items'][0]['statistics']['subscriberCount']
	tot_vids            =  response['items'][0]['statistics']['videoCount']
	created             = (response['items'][0]['snippet']['publishedAt']).split('T', 1)[0]
	bio                 =  response['items'][0]['snippet']['description']
	bio_length          = sum([len(str(bio[i])) for i, c in enumerate(bio)])
	bio_numbers         = sum(c.isdigit() for c in bio)
	bio_letters         = sum(c.isalpha() for c in bio)
	bio_spaces          = sum(c.isspace() for c in bio)
	bio_others          = bio_length - int(bio_numbers) - int(bio_letters) - int(bio_spaces)

	channel_info = pd.DataFrame([title, channelId, created, verf,  tot_subs, tot_views, tot_vids, channel_link,
								 profile_picture, bio, bio_length, bio_numbers, bio_letters, bio_spaces, bio_others], 
								index = ['username', 'channelId', 'created', 'Verification', 'tot_subs', 'tot_views',
										 'tot_vids', 'channel_link', 'profile_picture', 'bio', 'bio_length', 
										 'bio_numbers', 'bio_letters', 'bio_spaces', 'bio_others'], columns = ['Channel info'])
	return channel_info


def bio_counter(description):

			# description = str(description).strip('<meta content="')
			# description = description.strip('" name="description"/>')
			total = len(description)
			numbers = sum(c.isdigit() for c in description)
			letters = sum(c.isalpha() for c in description)
			spaces  = sum(c.isspace() for c in description)
			others  = total - numbers - letters - spaces
			bio = pd.DataFrame([total, numbers , letters , spaces,others], 
								index   = ['total characters', 'numbers' , 'letters' , 'spaces', 'others'], 
								columns = ['Bio breakdown'])
			return bio


# _______________________________________________________________ GET ALL VIDEOS LOOP ________________________________________________________________
def loop(youtube, ID, api_key):
	channelId = ID
	request = all_vids_loop(channelId, youtube)
	videofeed = pd.DataFrame()
	response = request.execute()
	resp_df, max_res = download(response)
	# print("_____________MAX_RES_____________")
	# print(max_res)
	# print(resp_df)
	videofeed = pd.concat([videofeed, resp_df], ignore_index = True)
	# response_list=[]
	while len(videofeed) < max_res:
		token = None
		try:
			response = request.execute()
			resp_df, max_res = download(response)
			# resp_df=pd.DataFrame(resp_df)

			# print("_____________VIDEOFEED_____________")
			# print(videofeed)
			# print("_____________RESP_DF_____________")
			# print(resp_df)
			# videofeed = pd.concat([videofeed, resp_df], ignore_index = True)
			videofeed = pd.concat([videofeed, resp_df], axis=0, ignore_index = True)
			# response_list.append(resp_df)
			request = youtube.search().list_next(request, response)
		except AttributeError:
			# print(videofeed)
			return videofeed
	# print(videofeed)
	return videofeed

def all_vids_loop(channelId, youtube):
	request = youtube.search().list(part = 'id,snippet',
									channelId = channelId,
									type = 'video',
									maxResults = 50,
									relevanceLanguage = 'en',)
	return request


def download(response):
	titles = []
	videoIds = []
	channelIds = []
	img = []
	date = []
	max_res = response['pageInfo']["totalResults"]
	resp_df = pd.DataFrame()
	for item in response['items']:
		titles.append(item['snippet']['title'])
		channelIds.append(item['snippet']['channelTitle'])
		videoIds.append(item['id']['videoId'])
		img.append(item['snippet']['thumbnails']['high']['url'])
		date.append(item['snippet']['publishTime'])
	if "nextPageToken" in response:
		print("..next page..")
		token = response["nextPageToken"]
		resp_df['date'] = date
		resp_df['channelId'] = channelIds
		resp_df['title'] = titles
		resp_df['videoId'] = videoIds
		resp_df['thumbnail'] = img
		return resp_df, max_res
	else:
		try:
			resp_df['date'] = date
			resp_df['channelId'] = channelIds
			resp_df['title'] = titles
			resp_df['videoId'] = videoIds
			resp_df['thumbnail'] = img
			print("..FINISHED!")
			return resp_df, max_res
		except:
			print("..FINISHED!")
			return resp_df, max_res
  

# __________________________________________________________________ GET VIDEO INFO __________________________________________________________________
def get_video_info(youtube, chunks):
	response = youtube.videos().list(part = "statistics,snippet",
									 id = chunks).execute()
	vid_info_list = []
	vid_info = pd.DataFrame()
	for i, ID in zip(response['items'], chunks):
		# print(i)
		if 'viewCount' in str(i['statistics']):
			viewCount = str(i['statistics']['viewCount'])
		else:
			viewCount = 0
		
		if 'likeCount' in str(i['statistics']):
			likeCount = str(i['statistics']['likeCount'])
		else:
			likeCount = 0		
		
		if 'commentCount' in str(i['statistics']):
			commentCount   = str(i['statistics']['commentCount'])
		else:
			commentCount = "no cmt."
		if 'tags' in str(i['snippet']):
			tags   = str(i['snippet']['tags'])
		else:
			tags = "no tags"
		if 'description' in str(i['snippet']):
			description   = str(i['snippet']['description'])
		else: 
			description = "no descr."
		df = pd.DataFrame([ viewCount,   likeCount,   commentCount,  tags,   description ], 
				  index = ['viewCount', 'likeCount', 'commentCount','tags', 'description'], 
				  columns=[ID]).T
		vid_info = pd.concat([vid_info, df], ignore_index = False)
	return vid_info



# _________________________________________________________________ DATAFRAME REWORK _________________________________________________________________
def Videofeed_Rework(videofeed):
	dates = list(videofeed.index)
	stripped = []
	for d in dates:
		date = d.split('T', 1)[0]
		stripped.append(date)
	videofeed = videofeed.set_index([stripped])
	videofeed.index = pd.to_datetime(videofeed.index)
	upload_rate = Upload_rate(videofeed)
	return videofeed, upload_rate

def Upload_rate(videofeed):
	now = dt.datetime.now()
	days60 = now - dt.timedelta(days = 60)
	now = re.sub(r'\s.*', '', str(now))
	days60 = re.sub(r'\s.*', '', str(days60))
	videofeed_60 = videofeed.loc[days60:]
	return(len(videofeed_60)/60)



# ________________________________________________________________________ Check Verification ______________________________________________________________________
def get_script(channelId):
	base = 'https://www.youtube.com/channel/{}/videos'
	soup_url = base.format(str(channelId))
	soup = BeautifulSoup(requests.get( soup_url, 
									   timeout=(100, 1000), 
									   headers=(Headers().generate()),
									   cookies={'CONSENT': 'YES+yt.410850881.no+FX+762'}).text, 
									  'html.parser' )
	scripts = soup.find_all("script") 
	script = scripts[32].text
	return script


def check_verification(channelId):
	script = get_script(channelId)
	if 'BADGE_STYLE_TYPE_VERIFIED' in script:
		return 'Verified'

	elif 'BADGE_STYLE_TYPE_VERIFIED' not in script:
		return 'NOT Verified'

	else:
		print('Error while checking: Verification Badge')
		return 'NaN'


def arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--Profile_info")
	parser.add_argument("-d", "--post_data")
	return parser.parse_args()





# ________________________________________________________________________ socialblade_export ______________________________________________________________________
def socialblade_export(api_key):
	return api_key


# def key_manager(msg):
	# api_keys = youtube_keys
	# try:
	# 	raise ValueError(msg)
	# except ValueError as e:  # as e syntax added in ~python2.5
	# 	if str(e) == "foo":
	# 		api_key = next(api_keys)
	# 		return api_key
	# 	else:
	# 		raise


# def key_manager():
	# account_used       = ""
	# insta_scraper_used = ""
	# print("=" * 100)
	# print()
	# print("initiate: Log in")
	# for i, api_key in enumerate(api_keys):
	# 	try:
	# 		Youtube(api_key)
	# 		print()
	# 		print(f'____ Trying api_key no.: {i} ____')
	# 		insta_scraper = Instagram_scraper(login_user, login_pass)
	# 		if insta_scraper:
	# 			print(f"log in successful")
	# 			print(f'    using account: {login_user}')
	# 			print()
	# 			insta_scraper_used = insta_scraper
	# 			account_used = login_user
	# 			break
	# 	except:
	# 		print(f'    Qouta is used up, trying next key..')
	# 		Youtube(next(api_key))
	# print(f"currently scraping from api_key no.: {i}")
	# return insta_scraper_used, account_used



# ORIGINAL CODE ORIGINAL CODE ORIGINAL CODE ORIGINAL CODE 
# def key_manager(url):
	# api_keys = youtube_keys
	# for i, api_key in enumerate(api_keys):
	# 	try:
	# 		print(api_key)
	# 		print(f'____ Trying api_key no.: {i} ____')
	# 		youtube = build('youtube', 'v3', developerKey = api_key)
	# 		print(f"__________________________________ Scraping Data from {username} __________________________________")
			

	# 		# 		 Calling Channel Scraper ___________
	# 		ID = get_channelId(youtube, url)
	# 		channel_info = get_channel_info(youtube, ID)
	# 		username = channel_info['Channel info']['username']
			

	# 		# 		 Calling Video Scraper ___________
	# 		videofeed = loop(youtube, ID, api_key)
	# 		videofeed = videofeed.reset_index(drop = True)
	# 		id_list = list(videofeed['videoId'])


	# 		chunks = [id_list[i:i + 50] for i in range(0, len(id_list), 50)]
	# 		vid_info = pd.DataFrame()
	# 		for chunk in chunks:
	# 			info_chunk = get_video_info(youtube, chunk)
	# 			vid_info = pd.concat([vid_info, info_chunk], ignore_index = False)
	# 		return channel_info, username, videofeed, vid_info
	# 		break

	# 	except:
	# 		print(f'    Qouta is used up, trying next key..')
	# print("You have used up the qouta for all of your keys,")
	# print('please wait 24 hours or refill "api_keys.txt" with more keys')
	# return None, None, None, None 
	# 		# Youtube(next(api_key))
# ORIGINAL CODE ORIGINAL CODE ORIGINAL CODE ORIGINAL CODE 



# def key_manager(url):




	



# ________________________________________________________________________ MAIN ______________________________________________________________________
def Youtube():
	# __________ Variables ___________
	args = arg_parser()
	print("=" * 100)
	print()
	print("initiate: Scraper")
	print()
	print("    "+"_" * 80)
	urls = []
	with open("url_list.txt","r") as file:
		for line in file:
			urls.extend(line.split())
	for url in urls:
		api_keys = youtube_keys
		for i, api_key in enumerate(api_keys):
			try:
				print(f'____ Trying api_key no.: {i} ____')
				youtube = build('youtube', 'v3', developerKey = api_key)
				# 		 Calling Channel Scraper ___________
				ID = get_channelId(youtube, url)
				socialblade_export(api_key)
				channel_info = get_channel_info(youtube, ID)
				username = channel_info['Channel info']['username']	
				print(f"__________________________________ Scraping Data from {username} __________________________________")
				# 		 Calling Video Scraper ___________
				videofeed = loop(youtube, ID, api_key)
				videofeed = videofeed.reset_index(drop = True)
				id_list = list(videofeed['videoId'])


				chunks = [id_list[i:i + 50] for i in range(0, len(id_list), 50)]
				vid_info = pd.DataFrame()
				for chunk in chunks:
					info_chunk = get_video_info(youtube, chunk)
					vid_info = pd.concat([vid_info, info_chunk], ignore_index = False)
				if channel_info.empty:
					print(f"process was stopped at {username}")
					print()
					print()
					print()
					break
				else: 
					print(f"successful scraped {username}")
					print() 
				tot_subs = channel_info['Channel info']['tot_subs']
			# __________ Edit Videofeed ___________
				videofeed = videofeed.set_index(['videoId'])
				videofeed = pd.concat([videofeed, vid_info], axis = 1, ignore_index = False)
				videofeed = videofeed.reset_index()
				videofeed['view/follow ratio'] = round((videofeed['viewCount'].astype(int)) / (int(tot_subs)),4) 
				videofeed = videofeed.set_index(['date'])
				videofeed = videofeed.sort_index(ascending = True)
				videofeed, Upload_rate = Videofeed_Rework(videofeed)
				videofeed = videofeed.rename(columns = {'index': 'videoId'})
				videofeed['video_link'] = "https://www.youtube.com/watch?v=" + videofeed['videoId']
				videofeed['description length'] = [len(str(videofeed['description'][i])) for i, des in enumerate(videofeed['description'])]
				videofeed['tags length'] = [len(str(videofeed['tags'][i])) for i, des in enumerate(videofeed['tags'])]
				feed_hex_df = top_colors(videofeed['thumbnail'])
				feed_hex_df = feed_hex_df.set_index(videofeed.index)
				videofeed = pd.concat((videofeed, feed_hex_df), axis=1)

			# __________ Edit Channel_info ___________
				Upload_rate = round(Upload_rate,4)
				df = pd.DataFrame([Upload_rate], index = ['Upload rate'], columns=['Channel info'])
				channel_info = pd.concat([channel_info, df], axis=0)
				channel_hex_df = top_colors_profile_pic(channel_info['Channel info']['profile_picture'])
				channel_info = pd.concat((channel_info, channel_hex_df), axis=0)


				# __________ Print Results ___________
				if args.Profile_info:        
					print()
					print()
					print(" --------------------------------------------------------------------  ")
					print(" |                        YOUTUBE PROFILE DATA                      |  ")
					print(" --------------------------------------------------------------------  ")
					print()
					print(channel_info)
					print("[ Warning; Due to subscriberCount being static, the Upload rate  ")
					print("  will be less accurate the further away we are from today.     ]")
				
				# __________Pandas Settings____________
				if args.post_data:
					pd.options.display.max_columns = None            
					pd.options.display.max_rows = 200             
					pd.options.display.max_colwidth = 20            
					pd.options.display.width = 2000
					print("_"*150)
					print()
					print(" --------------------------------------------------------------------  ")
					print(" |                         YOUTUBE VIDEO DATA                       |  ")
					print(" --------------------------------------------------------------------  ")
					print()
					print(videofeed)
					print("_"*150)

				## __________ Save All in zipfile ___________  
					path = r'output/'
					try:
						username = username.replace(" ", "")
						username = username.replace(" ", "").lower()
					except AttributeError:
						pass
					filepath = Path(f"{path}Youtube_data_{username}.zip")
					#renaming the variables
					profile_info = channel_info
					postfeed = videofeed
					profile_info = profile_info.reset_index()
					postfeed = postfeed.reset_index()
					if filepath.exists():
						with zipfile.ZipFile(f"{path}Youtube_data_{username}.zip", "a") as zf:
							if args.Profile_info:
								filename =  Path(f"{username}_profile_info.csv")
								if filename.exists():
									with zf.open(f"{username}_profile_info.csv", "w") as buffer:
										profile_info.to_csv(buffer, index = False)
								else:
									with zf.open(f"{username}_profile_info.csv", "w") as buffer:
										profile_info.to_csv(buffer, index = False)

							if args.post_data:
								filename =  Path(f"{username}_postdata.csv")
								if filename.exists():
									with zf.open(f"{username}_postdata.csv", "a") as buffer:
										postfeed.to_csv(buffer, index = False)
								else:
									with zf.open(f"{username}_postdata.csv", "w") as buffer:
										postfeed.to_csv(buffer, index = False) 
					else:
						with zipfile.ZipFile(f"{path}Youtube_data_{username}.zip", "w") as zf:
							if args.Profile_info:
								filename =  Path(f"{username}_profile_info.csv")
								if filename.exists():
									with zf.open(f"{username}_profile_info.csv", "w") as buffer:
										profile_info.to_csv(buffer, index = False)
								else:
									with zf.open(f"{username}_profile_info.csv", "w") as buffer:
										profile_info.to_csv(buffer, index = False)

							if args.post_data:
								filename =  Path(f"{username}_postdata.csv")
								if filename.exists():
									with zf.open(f"{username}_postdata.csv", "a") as buffer:
										postfeed.to_csv(buffer, index = False)
								else:
									with zf.open(f"{username}_postdata.csv", "w") as buffer:
										postfeed.to_csv(buffer, index = False) 
					print()   
					print(f"    file saved as: Youtube_data_{username}.zip, in: {path}")
					print("    "+"_" * 100)
				break
			except HttpError:
				print(f'    Qouta is used up, trying next key..')
			print("You have used up the qouta for all of your keys,")
			print('please wait 24 hours or refill "api_keys.txt" with more keys')
	print()
	print("exit: Scraper")

if __name__ == "__main__":
	Youtube()
	finish = time.perf_counter()
	print(f'Youtube Finished in {round(finish-start,2)} second(s)')
	messagebox.showinfo("Notification", "Youtube scraping is complete.")











