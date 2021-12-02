#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
from dateutil.tz import tzutc
import sys
import os
from urllib.request import urlretrieve
from pdf_analysis import make_formatted_top_songs

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path

path = home_path
python = python_path

# if len(sys.argv) != 2:
#     print("Please insert a month in mm-yyyy format!")

month = "11-2021"


# os.system(f"{python} {path}/get_rp.py >> {path}/newsongs.txt")
# os.system(f"rm {path}/newsongs.txt")


mode = "top_10"
tf = "dm"

redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)
#%%
# rp = sp.current_user_top_artists(limit = 50)
rp = sp.current_user_recently_played(limit = 50)

# %%
me = sp.current_user()
urlretrieve(me["images"][0]["url"],"myprofilepic.jpg")
# %%
import numpy as np
from PIL import Image, ImageDraw

img = Image.open("myprofilepic.jpg")
  
height,width = img.size
lum_img = Image.new('L', [height,width] , 0)
  
draw = ImageDraw.Draw(lum_img)
draw.pieslice([(0,0), (height,width)], 0, 360, 
              fill = 255, outline = "white")
img_arr = np.array(img)
lum_img_arr = np.array(lum_img)
final_img_arr = np.dstack((img_arr,lum_img_arr))

img = Image.fromarray(final_img_arr)
img.save("circprofilepic.png")

# %%
name = "My Wife & 2 Dogs"
