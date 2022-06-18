#____Count the time____
import time
start = time.perf_counter()

#____Regular imports____
import instagram_scraper
import pandas as pd
import datetime as dt
from datetime import date
from datetime import timedelta
from datetime import datetime
import argparse

#___ Unchecked imprts ______o
import re
import csv
import zipfile
from zipfile import ZipFile
from pathlib import Path
from pprint import pprint
import pprint 
from tkinter import messagebox


# __________ Local Imports ____________
from Color_counter import top_colors, top_colors_profile_pic
from Config import scraper_accounts, proxies


'''
________TO-DO__________
	"[X] means done"

	2.  [ ] Fix DATASAVER 
	3.  [ ] Clean up imports 
	4.  [ ] Create URL Loop
	5.  [ ] Create API Loop
	6.  [ ] Fill Youtube Requirements

	Youtube Requirements
		If you choose to scrape the account data it will create a csv file with:
		1. [X] The username
		2. [X] A link to the account
		3. [X] How many followers they have
		4. [X] How many posts they have
		5. [X] If they’re verified or not
		6. [X] How many characters (letters, symbols, etc.) are in their bio
		7. [X] If possible also find the dominant 3 colors of their profile picture and make that the color of 3 cells.
		8. [X] Count all of the posts created in the past 60 days and divide that number by 60.
				Last it should then search the account on social blade, a free website, and add this info:
		8. [X] Average number of follower growth per day.

		If you choose to scrape the post data:
		it should analyze all of their posts and all of them to the spreadsheet with the columns filled with:
		1. [X] A link to the post
		2. [X] Number of likes
		3. [X] Number of comments
		4. [X] The likes to followers % 
		5. [X] Number of characters in the post caption.
		6. [ ] Number of people tagged in the post. 
		7. [X] If it is an image the dominant 5 colors of that image in 5 separate cells as the 
				cells hex code color (this is intended to learn the color pallet of the photo)

		If you choose to have it scrape the follower data, it needs to the create a .csv spreadsheet
		that is filled with all of the people who follow that account with over 5,000 followers however 
		lim it the sheet to only 2,500 people with the most followers. On the spreadsheet it should give you:
		1. [ ] A link to the account
		2. [ ] The name of the account (@name)
		3. [ ] How many followers they have
		4. [ ] If they’re verified or not.
[       Open Me       ]
_______________________


________ BUGS _________
	1. [ ] Log-in failed:  
	2. [ ] "username-None" - bug: Usernames sometimes won't get scraped raising an error
	3. [ ] 

	Potential Fixes to "BUG 1.: Log-in failed":
		[ Open Me ]
			______________________________________ ARGS for  Instagram_scraper()  _________________________________

			default_attr = dict(username='', usernames=[], filename=None,
								login_user=None, login_pass=None,
								followings_input=False, followings_output='profiles.txt',
								destination='./', logger=None, retain_username=False, interactive=False,
								quiet=False, maximum=0, media_metadata=False, profile_metadata=False, latest=False,
								latest_stamps=False, cookiejar=None, filter_location=None, filter_locations=None,
								media_types=['image', 'video', 'story-image', 'story-video'],
								tag=False, location=False, search_location=False, comments=False,
								verbose=0, include_location=False, filter=None, proxies={}, no_check_certificate=False,
															template='{urlname}', log_destination='')


			# attr
			--cookiejar             File in which to store cookies so that they can be reused between runs.
			--profile-metadata      Saves the user profile metadata to  <destination>/<username>.json.
			--interactive -i       Enables interactive login challenge solving. Has 2 modes: SMS and Email
			--quiet       -q        Be quiet while scraping.



			# OTHER attr
			--proxies               Enable use of proxies, add a valid JSON with http or/and https urls.
									Example: '{"http": "http://<ip>:<port>", "https": "https://<ip>:<port>" }'
			--quiet       -q        Be quiet while scraping.
			--maximum     -m        Maximum number of items to scrape.
			--destination -d        Specify the download destination. By default, media will 
									be downloaded to <current working directory>/<username>.
			--followings-input      Use profiles followed by login-user as input
			--followings-output     Output profiles from --followings-input to file
			--filename    -f        Path to a file containing a list of users to scrape.
			--latest                Scrape only new media since the last scrape. Uses the last modified
									time of the latest media item in the destination directory to compare.

			NYTTIG !!!!! NYTTIG !!!!! NYTTIG !!!!! NYTTIG !!!!!
			--filename    -f        Path to a file containing a list of users to scrape.

			{'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36'}
			__________________________________________________________________________________________________________
[       Open Me       ]
_______________________

'''


# __________Pandas Settings____________
pd.options.display.max_columns = None
pd.options.display.max_rows=None
pd.options.display.width = 2000
pd.options.display.max_colwidth = 40


# _____________________________________________ PREPERATION ________________________________________________________
def Instagram_scraper(login_user, login_pass):
	# filename =  pd.read_csv(f"instagram_urls.csv")
	args = {"login_user": login_user, "login_pass": login_pass,
			'media_metadata':'True','profile_metadata':'True',
			'media_types':['image', 'video', 'story-image', 'story-video'],
			'comments':'True', 'cookiejar':'cookies.jar', 'proxies': proxies,} 
	insta_scraper = instagram_scraper.InstagramScraper(**args)
	insta_scraper.authenticate_with_login()
	return insta_scraper

def get_username(url):
	username = url.split('/')[3]
	return username


# _____________________________________________ ACCOUNT DATA _______________________________________________________

def Profile_info(shared_data, username):
	username            = shared_data['username']
	full_name           = shared_data['full_name']
	followers           = shared_data['edge_followed_by']['count']
	post_count          = shared_data['edge_owner_to_timeline_media']['count']
	Upload_rate         = ""
	verified            = shared_data['is_verified']
	bio                 = shared_data['biography']
	bio_length          = sum([len(str(bio[i])) for i, c in enumerate(bio)])
	bio_numbers         = sum(c.isdigit() for c in bio)
	bio_letters         = sum(c.isalpha() for c in bio)
	bio_spaces          = sum(c.isspace() for c in bio)
	bio_others          = bio_length - int(bio_numbers) - int(bio_letters) - int(bio_spaces)
	profile_picture     = shared_data['profile_pic_url_hd']
	link_to_account     =  f"https://www.instagram.com/{username}"

	profile_info = pd.DataFrame([username,full_name,followers,post_count,verified,
					   bio,bio_length,bio_numbers,bio_letters,bio_spaces,
					   bio_others,profile_picture,link_to_account], index =
					  ['username','full_name','followers','post_count','verified',
					   'bio','bio_length','bio_numbers','bio_letters','bio_spaces',
					   'bio_others','profile_picture','link_to_account'], columns = ['Profile info'])
	profile_hex_df = top_colors_profile_pic(profile_info['Profile info']['profile_picture'])
	profile_hex_df = profile_hex_df.rename(columns = {'Channel info':'Profile info'}) 
	profile_info   = pd.concat((profile_info, profile_hex_df), axis = 0)
	return profile_info, followers


# _____________________________________________ POST ______________________________________________________________

def post_data(shared_data, username, followers, insta_scraper):
	postfeed = pd.DataFrame()
	for item in insta_scraper.query_media_gen(shared_data):
		media_type            = item['__typename']
		date                  = datetime.utcfromtimestamp(item['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
		likes                 = item['edge_media_preview_like']['count']
		comments              = item['edge_media_to_comment']['count']
		if 'tags' in item:
			tags              = item['tags']
		else:
			tags              = '0'
		is_video              = item['is_video']
		if is_video==True:
			video_views       = item['video_view_count']
		else:
			video_views       = '0'
		if 'text' in item:
			description       = item['edge_media_to_caption']['edges'][0]['node']['text']
		else:
			description       = ""
		like_follow_ratio     = Like_follow_ratio(followers, likes)
		descr_length          = sum([len(str(description[i])) for i, c in enumerate(description)])
		descr_numbers         = sum(c.isdigit() for c in description)
		descr_letters         = sum(c.isalpha() for c in description)
		descr_spaces          = sum(c.isspace() for c in description)
		descr_others          = descr_length - int(descr_numbers) - int(descr_letters) - int(descr_spaces)
		image                 = item['display_url']
		link                  = f"https://www.instagram.com/p/{item['shortcode']}"

		df       = (pd.DataFrame([media_type, date, likes, comments, tags, video_views, 
								  description, like_follow_ratio, descr_length, 
								  descr_numbers, descr_letters, descr_spaces, descr_others, image, link], 
						 index = ['media_type', 'date', 'likes', 'comments', 'tags', 'video_views', 
								  'description', 'like_follow_ratio', 'descr_length', 
								  'descr_numbers', 'descr_letters', 'descr_spaces', 'descr_others', 'image/thumbnail', 'link to post'])).T
		postfeed = pd.concat([postfeed, df], axis = 0)
	feed_hex_df  = top_colors(postfeed['image/thumbnail'])
	feed_hex_df  = feed_hex_df.set_index(postfeed.index)
	postfeed     = pd.concat((postfeed, feed_hex_df), axis = 1)
	return postfeed



# ___________________________________________________ REWORK ______________________________________________________
def Like_follow_ratio(followers, likes):
	try:
		return round((likes.astype(int)) / (int(followers)),4)
	except AttributeError:
		try:
			return round((likes / (int(followers))),4) 
		except AttributeError:
			return round((likes / followers) ,4) 

def Upload_rate(postfeed):
	now = dt.datetime.now()
	days60 = now - dt.timedelta(days = 60)
	now = re.sub(r'\s.*', '', str(now))
	days60 = re.sub(r'\s.*', '', str(days60))
	postfeed_60 = postfeed.loc[days60:]
	return(len(postfeed_60)/60)


# ____________________________________________________ MAIN ________________________________________________________

def log_in_traficker():
	account_used       = ""
	insta_scraper_used = ""
	print("=" * 100)
	print()
	print("initiate: Log in")
	for i, account in enumerate(scraper_accounts):
		try:
			login_user = account[0]
			login_pass = account[1]
			print()
			print(f'____checking {login_user}____')
			insta_scraper = Instagram_scraper(login_user, login_pass)
			if insta_scraper:
				print(f"log in successful")
				print(f'    using account: {login_user}')
				print()
				insta_scraper_used = insta_scraper
				account_used = login_user
				break
		except:
			print(f'    trying next..')
			pass
	print(f"currently scraping from account: {account_used}")
	print()
	print("exit: Log in")
	print("=" * 100)
	return insta_scraper_used, account_used

def arg_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--Profile_info")
	parser.add_argument("-d", "--post_data")
	return parser.parse_args()


def Instagram():
	# __________ Variables ___________
	args = arg_parser()
	insta_scraper, account_used = log_in_traficker()
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
		print(url)
		username = get_username(url)
	# __________ scraper ___________
		time.sleep(1)
		shared_data = insta_scraper.get_shared_data_userinfo(username = username)
		print(f"    CURRENTLY SCRAPING: {username}")
		print(f"        try: scraping data for {username}..")
	## Checking is shared_data is empty (if statement)
		# while True:  
		if not shared_data:
			print(f"            Error: download failed, did not find shared_data on {username}")
			time.sleep(0.1)
			## [retry script]
			print(f"            ..trying again")
			print(f"            .. waiting 1 second")
			time.sleep(1)
			print(f"    retrying to fetch shared_data on {username}..")
			# shared_data, insta_scraper = get_shared_data(username, login_user, login_pass)
			shared_data = insta_scraper.get_shared_data_userinfo(username = username)
		else:
			print(f"    succsess, found shared_data on {username}")
			print(f'         proof: printing "shared_data["full_name"]"   --> ' + shared_data['full_name'])
			print(f"         downloading..")
			
			## [scraping script]    
			profile_info, followers = Profile_info(shared_data, username)
			postfeed = post_data(shared_data, username, followers, insta_scraper)

			## postfeed rework:
			upload_rate  = round(Upload_rate(postfeed),4)
			upload_rate  = pd.DataFrame([upload_rate], index = ['Upload_rate'], columns = ['Profile info'])
			profile_info = pd.concat([profile_info, upload_rate], axis = 0)
			
			## __________ Print Results ___________        
			if args.Profile_info:
				print()
				print("     --------------------------------------------------------------------  ")
				print("     |                      INSTAGRAM PROFILE DATA                      |  ")
				print("     --------------------------------------------------------------------  ")
				print()
				print(profile_info)
				print("     [ Warning; Due to subscriberCount being static, the Upload rate  ")
				print("         will be less accurate the further away we are from today.     ]")

			if args.post_data:
				pd.options.display.max_columns = 5            
				pd.options.display.max_rows = 5             
				pd.options.display.max_colwidth = 20            
				pd.options.display.width = 2000
				print()
				print("     --------------------------------------------------------------------  ")
				print("     |                        INSTAGRAM FEED DATA                       |  ")
				print("     --------------------------------------------------------------------  ")
				print()
				print(postfeed)
 
			## __________ Save All in zipfile ___________  
			profile_info = profile_info.reset_index()
			postfeed = postfeed.reset_index()
			path = r'output/'
			filepath =  Path(f"{path}Instagram_data_{username}.zip")
			if filepath.exists():
				with zipfile.ZipFile(f"{path}Instagram_data_{username}.zip", "a") as zf:
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
				with zipfile.ZipFile(f"{path}Instagram_data_{username}.zip", "w") as zf:
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
	print(f"    file saved as: Instagram_data_{username}.zip, in: {path}")
	print("    "+"_" * 100)
		# break
	print()
	print("exit: Scraper")
	


if __name__ == "__main__":
	Instagram()
	finish = time.perf_counter()
	print(f'Finished in {round(finish - start, 2)} second(s)')
	print("=" * 80)
	messagebox.showinfo("Notification", "Instagram scraping is complete.")