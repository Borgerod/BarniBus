#_______________ INSTAGRAM _______________
# Make instagram account or use your own and fill in USERNAME & PASSWORD:
scraper_accounts = [

['USERNAME','PASSWORD'],
['USERNAME','PASSWORD'],
['USERNAME','PASSWORD'],

                   ]
# Proxy:
proxies = { 'http'  : 'http://10.10.1.10:3128', 
            'https' : 'https://10.10.1.11:1080', 
            'ftp'   : 'ftp://10.10.1.10:3128',}


#_______________ SOCIALBLADE _______________
# Make a socialblade account and fill in USERNAME & PASSWORD:
socialblade_payload = {'inUserName': 'USERNAME','inUserPass': 'PASSWORD'}

# cookies:
socialblade_cookies = {'__asc' :'b5c0fe4917fd413e6b30b30da6e',
                       '__auc': 'b5c0fe4917fd413e6b30b30da6e',
                       '__qca' : 'P0-1854281166-1648530548847',
                       '_gat_socialblade' : '1',
                       '_ga' : 'GA1.2.1146866666.1648530549',
                       '_gid ': 'GA1.2.1658963366.1648530549',
                       'lngtd-sdp' :'9',
                       'PHPSESSXX' :'4hg5p5gotm3ng77p3uh9hfrmag',}


#_______________ TIKTOK _______________
# verify_fp need to be changed regurarly, so if tiktok scraper isn't working it is because of this.
# in the instructions you will find a tutorial video. Simply replace the old one with a new one.
verify_fp = 'verify_9b5b6d6b1b3c51b61d3b06a5dade1eea'
