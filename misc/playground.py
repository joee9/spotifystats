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
from os.path import exists
from urllib.request import urlretrieve

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path

import json

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

print(rp["items"][0])

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

my = "12-2021"
path = f"{home_path}/data"
df = pd.read_csv(path + f"/{my}-songlist.txt")

if not exists(f"{path}/{my}-database.txt"):
    # db = pd.DataFrame(columns = ["ID", "name", "ArtistIDs", "ArtistNames", "PicURL"])
    db = {}

else:
    with open(f"{path}/{my}-database.txt", "r") as f:
        db = json.loads(f.read())

for song in rp["items"]:
    id = song["track"]["id"]
    if id in db:
        name = db[id]["name"]
        artist_ids = db[id]["ArtistIDs"]
        artist_names = db[id]["ArtistNames"]
        pic_url = db[id]["PicURL"]
    else:
        track = sp.track(id)
        artist_ids = []
        artist_names = []
        for artist in track["album"]["artists"]:
            artist_ids.append(artist["id"])
            artist_names.append(artist["name"])
        name = track["name"]
        pic_url = track["album"]["images"][1]["url"]

        # db = db.append([[id, name, artist_ids, artist_names, pic_url]], columns=)
        db[id] = {"name": name,
            "ArtistIDs": artist_ids,
            "ArtistNames": artist_names,
            "PicURL": pic_url
        }

with open(f"{path}/{my}-database.txt","a") as output:
    output.write(json.dumps(db))


# counts = df["URI"].value_counts()
# keys = counts.keys()[0:10]

# sorted = []
# for key in keys:
#     name = sp.track(key)["name"]
#     sorted.append({"name": name, "URI": key, "count": counts[key]})

# def sort_by_name(d): return -d["count"], d["name"]

# sorted.sort(key=sort_by_name)

# sorted_keys = []
# for entry in sorted:
#     sorted_keys.append(entry["URI"])

# print(sorted, sorted_keys)




# %%
uri = "4T6FWA703h6H7zk1FoSARw"
track = sp.track(uri)

#%%
d1 = {"a": 1, "b": 2}
d2 = {"a": 3, "d": 4}

d1.update(d2)

print(d1)

#%%
uri = "4LLpKhyESsyAXpc4laK94U"
artist = sp.artist(uri)
# %%
uri = "5wtE5aLX5r7jOosmPhJhhk"
album = sp.album(uri)
# %%
