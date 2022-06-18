import cv2
import numpy as np
import urllib.request
import pandas as pd 


# _____________________________ VARIABLES ___________________________________________________________________________________________
def variables():                                                                # Contains images and decides amount of dom-colors
    number_clusters = 5                                                         # Amount of dominant colors you want 
    return number_clusters#, img_url

# _____________________________ IMPORT & PREPERATION ________________________________________________________________________________
def import_img(url):                                                            # Import image
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1) # 'Load it as it is'
    return img


# _______________________________ FINDING DOMINANT _________________________________________________________________________________
def find_dominants(img, number_clusters):                                        # Creates bars, and rgb_values by using create_bar()
    height, width, _ = np.shape(img)                                             # Reshape
    data = np.reshape(img, (height * width, 3))
    data = np.float32(data)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags    =  cv2.KMEANS_RANDOM_CENTERS
    _, _, centers = cv2.kmeans(data, number_clusters, 
                                              None, criteria, 10, flags)  
    return centers 

# _____________________________ CREATE VIUSALS  ____________________________________________________________________________________

def make_RGB_and_HEX(centers):                                                  # Calls create_bar(), then puts bar & rgb into lists                                                                 # Dominant colors are added to img_bar
    rgb_values = []                                                             # Makes RGB values and add it to rgb_value
    for color in centers:
        rgb = (int(color[2]), int(color[1]), int(color[0]))
        rgb_values.append(rgb)
    hex_values = []
    for rgb in rgb_values:
        hex_ = '{}%02x%02x%02x' % rgb
        hex_ = hex_.format('#')
        hex_values.append(hex_)
    return rgb_values, hex_values



# _______________________________________ MAIN _____________________________________________________________________________________
def top_colors(videofeed_input):
    img_url = videofeed_input 
    number_clusters = variables()   
    # number_clusters, img_url = variables()                                      # get variables 
    all_hex_values  = []
    # all_rgb_values  = []
    for url in img_url:
        img = import_img(url)                                                   # import img
        centers = find_dominants(img, number_clusters)                          # find dominant colors  
        rgb_values, hex_values = make_RGB_and_HEX(centers)                      # make rgb and hex 

        # all_rgb_values.append(rgb_values)
        all_hex_values.append(hex_values)
        

    # # Make rgb dataframe
    # dominant_colors_rgb = pd.DataFrame(all_rgb_values, columns = ['Top colors: no. 1','no. 2','no. 3','no. 4','no. 5',])


    # Make hex dataframe
    dominant_colors_hex = pd.DataFrame(all_hex_values, columns = ['Top colors: no. 1','no. 2','no. 3','no. 4','no. 5',])               
    return dominant_colors_hex

# if __name__ == '__main__' :
#     top_colors(videofeed_input)


def top_colors_profile_pic(channel_info_input):
    url = channel_info_input 
    number_clusters = variables()   
    all_hex_values  = []
    # all_rgb_values  = []
    img = import_img(url)                                                   # import img
    centers = find_dominants(img, number_clusters)                          # find dominant colors  
    rgb_values, hex_values = make_RGB_and_HEX(centers)                      # make rgb and hex 

    # all_rgb_values.append(rgb_values)
    all_hex_values.append(hex_values)
        

    # # Make rgb dataframe
    # dominant_colors_rgb = pd.DataFrame(all_rgb_values, columns = ['Top colors: no. 1','no. 2','no. 3','no. 4','no. 5',])


    # Make hex dataframe
    dominant_colors_hex = pd.DataFrame(all_hex_values, index = ['Channel info'], columns = ['Top color: no. 1','Top color: no. 2','Top color: no. 3','Top color: no. 4','Top color: no. 5',]).T        
    
    return dominant_colors_hex    



