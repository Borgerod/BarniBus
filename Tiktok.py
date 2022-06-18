'''
________TO-DO__________
	"[X] means done"

	1.  [ ] 
	2.  [ ] 
	3.  [ ] 
	4.  [ ] 
	5.  [ ] 
	6.  [ ] Fill TikTok Requirements
		TIKTOK CHANNEL REQUIREMENTS:

			_______ ACCOUNT DATA ______
			If you choose to scrape the account data it will create a csv file with:
				1. [X] The username
				2. [X] A link to the account
				3. [X] How many followers they have
				4. [X] How many posts they have
				5. [X] If they’re verified or not
				6. [X] How many characters (letters, symbols, etc. [ ]) are in their bio
				7. [X] If possible also find the dominant 3 colors of their profile picture and make that the color of 3 cells.
				8. [X] Count all of the posts created in the past 60 days and divide that number by 60.
			
			_______ POST DATA ______ 
			If you choose to scrape the post data it should analyze all of their posts 
				and add all of them to the spreadsheet with the columns filled with:
				1. [X] A link to the post
				2. [X] Number of views
				3. [X] Number of likes
				4. [X] Number of comments
				5. [X] The views to followers % (how many views the post has in comparison to how many followers the account has.
						So for example if they have 100,000 followers and get 10,000 views, the cell should read 10%)
				6. [X] Number of characters in the post caption.
				7. [X] Number of people tagged in the caption.
				8. [X] The number of hashtags in the caption.

			_______ FOLLOWER DATA ______ 
			If you choose to have it scrape the follower data, it needs to the create a .csv spreadsheet 
				that is filled with all of the people who follow that account with over 5,000 followers 
				however limit the sheet to only 2,500 people with the most followers. 
				On the spreadsheet it should give you:
				1. [ ] A link to the account
				2. [ ] The name of the account (@name)
				3. [ ] How many followers they have
				4. [ ] If they’re verified or not. [ ]
[       Open Me       ]
_______________________

________ BUGS _________
	1. [ ] 
	2. [ ] 
	3. [ ] 			
[       Open Me       ]
_______________________

'''


#____Count the time____
import time
start = time.perf_counter()


#____Regular imports____
import pandas as pd 
from TikTokApi import TikTokApi
import pprint
import re
import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime
import zipfile
from zipfile import ZipFile
from pathlib import Path
import argparse
from tkinter import messagebox


# __________ Local Imports ____________
from Color_counter import top_colors, top_colors_profile_pic
from Config import scraper_accounts, proxies, verify_fp


# __________Pandas Settings____________
pd.options.display.max_columns = None            
# pd.options.display.max_rows = None              
# pd.options.display.max_colwidth = 20            
pd.options.display.width = 2000



# ______________________________________________ API / PREPERATION ________________________________________________
def Api():
	api = TikTokApi(custom_verify_fp=verify_fp)
	return api

def get_usernames(urls):
	usernames = link_to_variable(urls)
	return usernames

def get_count():
	count=100
	return count


def link_to_variable(url):
	usernames = (url.split('/'))[3]
	usernames = (url.split('@'))[1] 
	return usernames




# ______________________________________________ ACCOUNT INFO _____________________________________________________
def get_profiles(api, username):
	dict_list=api.user(username).info_full()
	return dict_list, username

def profile_dict(tiktok_dict):
	to_return                       = {}
	to_return['user_name']          = tiktok_dict['user']['uniqueId']
	to_return['user_id']            = tiktok_dict['user']['id']
	to_return['created']            = datetime.utcfromtimestamp(tiktok_dict['user']['createTime']).strftime('%Y-%m-%d %H:%M:%S')
	to_return['profile_link']       = 'https://www.tiktok.com/@{}'.format(to_return['user_name'])   
	to_return['n_likes']            = tiktok_dict['stats']['heartCount']
	to_return['n_followers']        = tiktok_dict['stats']['followerCount']
	to_return['n_posts']            = tiktok_dict['stats']['videoCount']
	to_return['verified']           = tiktok_dict['user']['verified']
	to_return['bio']                = tiktok_dict['user']['signature']
	to_return['bio_length']         = sum([len(str(to_return['bio'][i])) for i, c in enumerate(to_return['bio'])])
	to_return['bio_numbers']        = sum(c.isdigit() for c in to_return['bio'])
	to_return['bio_letters']        = sum(c.isalpha() for c in to_return['bio'])
	to_return['bio_spaces']         = sum(c.isspace() for c in to_return['bio'])
	to_return['bio_others']         = to_return['bio_length'] - int(to_return['bio_numbers']) - int(to_return['bio_letters']) - int(to_return['bio_spaces'])
	to_return['profile_picture']    = tiktok_dict['user']['avatarLarger']
	return to_return



def profile_data(api,username):
	dict_list, username= get_profiles(api, username)
	profile_info = profile_dict(dict_list)
	profile_info = pd.DataFrame(profile_info,
								  columns = ['user_name','user_id','created','profile_link', 'n_likes',
											'n_followers','n_posts','verified','bio','bio_length', 'bio_numbers', 
											'bio_letters', 'bio_spaces', 'bio_others','profile_picture',], 
								  index   = ['Profile info']).T
	profile_hex_df = top_colors_profile_pic(profile_info['Profile info']['profile_picture'])
	profile_hex_df = profile_hex_df.rename(columns = {'Channel info':'Profile info'}) 
	profile_info   = pd.concat((profile_info, profile_hex_df), axis = 0)
	return profile_info



#_____________________________________________ SCRAPING POST DATA _________________________________________________
def get_feed(api, count, username):
	# for username in usernames:
	user_videos = api.user(username).videos(count=count)
	dict_list = []
	for video in user_videos:
		tiktok_dict = video.as_dict
		dict_list.append(tiktok_dict)
	return dict_list


def feed_dict(tiktok_dict):
	to_return                           = {}
	to_return['user_name']              = tiktok_dict['author']['uniqueId']
	to_return['user_id']                = tiktok_dict['author']['id']
	to_return['video_id']               = tiktok_dict['id']
	to_return['description']            = tiktok_dict['desc']
	to_return['descr_length']           = sum([len(str(to_return['description'][i])) for i, c in enumerate(to_return['description'])])
	to_return['descr_numbers']          = sum(c.isdigit() for c in to_return['description'])
	to_return['descr_letters']          = sum(c.isalpha() for c in to_return['description'])
	to_return['descr_spaces']           = sum(c.isspace() for c in to_return['description'])
	to_return['descr_others']           = to_return['descr_length'] - int(to_return['descr_numbers']) - int(to_return['descr_letters']) - int(to_return['descr_spaces'])
	to_return['date']                   = datetime.utcfromtimestamp(tiktok_dict['createTime']).strftime('%Y-%m-%d %H:%M:%S')
	to_return['video_lenth_(s)']        = tiktok_dict['video']['duration']
	to_return['video_link']             = 'https://www.tiktok.com/@{}/video/{}?land=en'.format(to_return['user_name'],to_return['video_id'])
	to_return['likes']                  = tiktok_dict['stats']['diggCount']
	to_return['shares']                 = tiktok_dict['stats']['shareCount']
	to_return['comments']               = tiktok_dict['stats']['commentCount']  
	to_return['plays']                  = tiktok_dict['stats']['playCount']
	to_return['thumbnail']              = tiktok_dict['video']['cover']
	if 'textExtra' in tiktok_dict:
		to_return['hashtag']            = [i['hashtagName'] for i in tiktok_dict['textExtra']]
		to_return['n_hashtag']          = len(to_return['hashtag'])
	if 'encodeUserTag' in tiktok_dict:
		to_return['UserTag']            = [i for i in tiktok_dict['video']['encodeUserTag']]
	if 'stickersOnItem' in tiktok_dict:
		to_return['screen_text']        = ((tiktok_dict['stickersOnItem'][0]['stickerText'][0]).replace("\n", " ")) 
	to_return['Like_follow_ratio']      = round( (to_return['likes']) /   (tiktok_dict['authorStats']['followerCount']),2)
	return to_return


def Post_data(api, count, username):
	vid_dict_list = get_feed(api, count, username)
	user_videos = [feed_dict(tiktok_dict) for tiktok_dict in vid_dict_list]
	postfeed = pd.DataFrame(user_videos,
							columns = [ 'user_name','user_id','video_id','date','video_lenth_(s)',
										'video_link','likes','shares','comments','Like_follow_ratio','plays','description',
										'descr_length', 'descr_numbers', 'descr_letters', 'descr_spaces',   
										'descr_others','thumbnail', 'hashtag', 'n_hashtag', 'UserTag', 'screen_text'])


	feed_hex_df = top_colors(postfeed['thumbnail'])
	feed_hex_df = feed_hex_df.set_index(postfeed.index)
	postfeed    = pd.concat((postfeed, feed_hex_df), axis = 1)
	return postfeed



# ___________________________________________________ REWORK ______________________________________________________

def Upload_rate(post_data):
	now = dt.datetime.now()
	days60 = now - dt.timedelta(days = 60)
	now = re.sub(r'\s.*', '', str(now))
	days60 = re.sub(r'\s.*', '', str(days60))
	postfeed_60 = post_data.loc[days60:]
	return(len(postfeed_60)/60)





# __________________________________________________ MAIN _________________________________________________________

def arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--Profile_info")
	parser.add_argument("-d", "--post_data")
	return parser.parse_args()



def Tiktok():
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
		count = get_count()
		username = get_usernames(url)
	# __________ scraper ___________
		# API CALL
		api = Api()

		# POST DATA
		post_data=Post_data(api, count, username)

		# PROFILE DATA
		profile_info = profile_data(api, username)

		# PROFILE DATA REWORK 
		upload_rate  = round(Upload_rate(post_data),4)
		upload_rate  = pd.DataFrame([upload_rate], index = ['Upload_rate'], columns = ['Profile info'])
		profile_info = pd.concat([profile_info, upload_rate], axis = 0)

		## __________ Print Results ___________
		if args.Profile_info:        
			print()
			print("     --------------------------------------------------------------------  ")
			print("     |                      TIKTOK PROFILE DATA                         |  ")
			print("     --------------------------------------------------------------------  ")
			print()
			print(profile_info)
			print("     [ Warning; Due to subscriberCount being static, the Upload rate    ")
			print("         will be less accurate the further away we are from today.     ]")
		if args.post_data:
			pd.options.display.max_columns = 5            
			pd.options.display.max_rows = 5             
			pd.options.display.max_colwidth = 20            
			pd.options.display.width = 2000
			print()
			print("     --------------------------------------------------------------------  ")
			print("     |                        TIKTOK FEED DATA                          |  ")
			print("     --------------------------------------------------------------------  ")
			print()
			print(post_data)

		## __________ Save All in zipfile ___________  
		postfeed = post_data
		path = r'output/'
		filepath =  Path(f"{path}TikTok_data_{username}.zip")
		postfeed = post_data
		profile_info.reset_index()
		postfeed.reset_index()
		if filepath.exists():
			with zipfile.ZipFile(f"{path}TikTok_data_{username}.zip", "a") as zf:
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
			with zipfile.ZipFile(f"{path}TikTok_data_{username}.zip", "w") as zf:
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
		print(f"    file saved as: Tiktok_data_{username}.zip, in: {path}")
		print("    "+"_" * 100)

	print()
	print("exit: Scraper")



if __name__ == '__main__':
	Tiktok()
	finish = time.perf_counter()
	print(f'Finished in {round(finish - start, 2)} second(s)')
	messagebox.showinfo("Notification", "Tiktok scraping is complete.")
