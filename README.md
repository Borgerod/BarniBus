# Barnibus - Social media data extraction software
[Previous Upwork Job] as developer, where I built a user friendly data extraction application for a small business, in two weeks.


## Summary
- Job Completed:  April 2022
- Job type:				Development 
- Job categogy:		Desktop Application, Data Extraction
- Language:				Python
- Style:          Functional & Object Oriented


## Project description
### Input 
The goal of the project was this; create a platform that scrapes these three social medias:
- Instagram
- Youtube
- TikTok
Additionally you would have the choice to scrape these types of data:
- Account data
- Upload/post data
- Socialblade data

The program should also have an AI that would find the dominant colors for every scraped photo.
Lastly, since my clients were not familiar with coding, the program should have a graphical user interface (GUI) and be compiled into a .exe file for easy usage with no installs.

### Output
The output should be saved in a ZIP file where each dataframe should be individually after its function and the username of the "target".
The requirements for the output was different for each platform, but overall:

- posts_data:
[generic] likes, comments, views, shares, thumbnails, description, date, @tags, #tags, etc..
[special] like-to-follow ratio, number of words and special characters in the description, and the
top 5 colors used in the post/thumbnail.

- profile_data:
[generic] total likes, followers, following, avatar, bio, date of creation, verification badge, etc..
[special] 60-day Upload rate, number of words and special characters in the bio, and the
top 5 colors used in the post/thumbnail.

- Socialblade_data:
Socialblade data should include these 8 dataframes:
- The top information
- The summary
- The ranks
- All of the averages
- All of the charts
- The data table
- 
## Relevant Screenshots [Project description]
### The UI: 
![image](https://user-images.githubusercontent.com/97392841/174436519-6a77c87c-8145-4edd-87fe-a718b844d64e.png)

### Code snippets:
![image](https://user-images.githubusercontent.com/97392841/174436539-8ac0697f-1cad-4d0f-8390-11645e389c90.png)

### The user instruction:
![image](https://user-images.githubusercontent.com/97392841/174436556-30faefb4-ced6-497a-b246-7f636dcc90c7.png)

### the file output:
![image](https://user-images.githubusercontent.com/97392841/174436573-4b26a31b-b8cd-442e-88b9-52be7b6194b3.png)

### Upload data:
![image](https://user-images.githubusercontent.com/97392841/174436652-06265317-4b94-4364-9d41-c40ee0711165.png)
### Profile data:
![image](https://user-images.githubusercontent.com/97392841/174436653-38189e84-5607-41da-b2db-5115ab21c1be.png)
### Socialblade Data
![image](https://user-images.githubusercontent.com/97392841/174436662-f7d363cf-800f-4c7f-85d2-ef9b984595f7.png)
![image](https://user-images.githubusercontent.com/97392841/174436664-c5a0d42f-dba2-4743-bc81-49e7cb3fbfc2.png)
![image](https://user-images.githubusercontent.com/97392841/174436682-b24a9ed8-2495-4d9c-b220-fd846da80d11.png)



## Solution & Challanges
Since the social medias are using very different platforms, I had to use a different method for each of them. They were all challanging in their own way, but I found tiktok and Socialblade to be especially hard, due to security measurements such as catchpa and cloudflare.
I dealt with cloudflare by implementing proxies, fake headers and a series of cookies to my requests. The catchpa however was a bit more difficult, I solved the issue by fetching the temporary verification-token, you recieve after solving the puzzle, which you can then add to the other cookies, gaining access.

Socialblade had another challange for me, since they both html and javascript in their code. Since I don't know any javascript I had to learn a bit of it and then find a way for my python code to read javascript so it could extract the code from it. A simple library named "js2py" did the trick nicely.

Instagram had a different challange for me where they have made it impossible to access their paltform without being a physical user. I solved this by using a web crawler library, along with the login info for instagram accounts, and a function that would switch to another account whenever instagram detected the suspicious activity.

Youtube actually has an api which was a breath of fresh air, however, their api has a daily qouta, which was way too small to be usefull bare in mind. But since you can make 10 google accounts pr phone number, I fixed the issue by doing that, then creating one api key each, and then applied the same revelotuion-function to it.

I have some experience with AI development so making the color-ranker was not that hard, though those things aren't very fun to setup.

As mainly a backend programmer using a backend programming language, making a front end program is quite the drag.

Now you might don't know this but python is not a programming language designed to be turned into a app (exe file), and you have to do a serious workaround in order to make it work.

## Relevant Screenshots [Solutuion & Challanges]
### The Cookie challange for accsessing Tiktok
![image](https://user-images.githubusercontent.com/97392841/174436778-1a332e7d-446e-433c-affe-c78ecbdf3a9c.png)


