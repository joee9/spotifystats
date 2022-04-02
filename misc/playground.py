#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
from dateutil.tz import tzutc
import sys
import os
from os.path import exists
from urllib.request import urlretrieve
import json
#%%

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path


#%%

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

print(rp["items"][49])

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
import matplotlib.pyplot as plt
ts=['2022-01-01T05:30:00.020Z', '2022-01-01T05:38:21.269Z', '2022-01-01T05:46:19.664Z', '2022-01-01T05:49:01.103Z', '2022-01-01T05:53:07.632Z', '2022-01-01T05:57:56.047Z', '2022-01-01T17:10:58.992Z', '2022-01-01T17:15:04.571Z', '2022-01-01T17:21:38.234Z', '2022-01-01T17:26:21.469Z', '2022-01-01T17:35:22.667Z', '2022-01-02T04:37:40.506Z', '2022-01-02T04:45:05.640Z', '2022-01-02T04:49:57.215Z', '2022-01-02T05:05:22.221Z', '2022-01-02T05:16:46.008Z', '2022-01-02T05:31:31.981Z', '2022-01-02T05:36:24.789Z', '2022-01-02T05:42:07.374Z', '2022-01-02T06:03:13.028Z', '2022-01-02T06:17:59.940Z', '2022-01-02T06:22:52.832Z', '2022-01-02T17:37:05.645Z', '2022-01-03T02:00:51.938Z', '2022-01-03T15:48:30.947Z', '2022-01-03T15:51:13.040Z', '2022-01-03T15:59:00.016Z', '2022-01-03T21:32:30.907Z', '2022-01-03T21:47:45.075Z', '2022-01-03T21:53:41.512Z', '2022-01-03T21:58:34.713Z', '2022-01-04T14:49:11.734Z', '2022-01-04T16:18:21.107Z', '2022-01-04T18:19:53.219Z', '2022-01-04T18:24:41.143Z', '2022-01-04T19:09:23.962Z', '2022-01-04T19:15:52.038Z', '2022-01-04T19:25:08.093Z', '2022-01-04T19:41:39.697Z', '2022-01-04T19:46:45.870Z', '2022-01-04T21:19:43.143Z', '2022-01-05T17:45:41.007Z', '2022-01-05T17:48:28.741Z', '2022-01-05T17:55:14.218Z', '2022-01-05T20:28:51.572Z', '2022-01-05T20:40:44.703Z', '2022-01-05T21:37:12.533Z', '2022-01-05T21:45:45.273Z', '2022-01-06T05:24:58.713Z', '2022-01-06T14:37:09.688Z', '2022-01-06T14:41:58.946Z', '2022-01-06T17:38:33.178Z', '2022-01-06T21:24:28.716Z', '2022-01-06T21:28:35.017Z', '2022-01-06T21:33:47.594Z', '2022-01-06T21:37:23.012Z', '2022-01-06T21:43:08.140Z', '2022-01-07T05:02:49.325Z', '2022-01-07T16:46:53.010Z', '2022-01-07T17:02:27.820Z', '2022-01-07T17:17:14.615Z', '2022-01-07T17:46:51.699Z', '2022-01-07T17:51:58.102Z', '2022-01-07T20:44:38.088Z', '2022-01-07T20:49:28.397Z', '2022-01-07T20:54:17.008Z', '2022-01-07T20:58:13.015Z', '2022-01-07T21:04:35.105Z', '2022-01-07T21:08:45.078Z', '2022-01-07T21:13:32.848Z', '2022-01-07T21:18:14.541Z', '2022-01-07T21:21:45.031Z', '2022-01-07T21:25:42.117Z', '2022-01-07T21:31:27.008Z', '2022-01-07T21:37:16.390Z', '2022-01-08T16:36:56.015Z', '2022-01-09T06:58:59.586Z', '2022-01-09T16:51:25.971Z', '2022-01-09T17:28:01.884Z', '2022-01-10T02:19:21.204Z', '2022-01-10T17:26:41.869Z', '2022-01-10T17:32:06.483Z', '2022-01-11T00:44:58.401Z', '2022-01-11T14:17:01.653Z', '2022-01-11T14:20:54.167Z', '2022-01-11T14:24:23.343Z', '2022-01-11T14:30:08.531Z', '2022-01-11T14:33:49.842Z', '2022-01-11T14:38:06.017Z', '2022-01-11T14:42:52.398Z', '2022-01-11T17:24:23.736Z', '2022-01-11T17:24:53.208Z', '2022-01-12T13:04:29.434Z', '2022-01-12T13:12:08.158Z', '2022-01-12T15:46:16.454Z', '2022-01-12T15:50:29.348Z', '2022-01-12T15:55:17.641Z', '2022-01-12T15:58:53.016Z', '2022-01-12T16:04:38.012Z', '2022-01-12T16:08:49.013Z', '2022-01-12T16:13:36.019Z', '2022-01-12T16:18:07.004Z', '2022-01-12T16:21:37.274Z', '2022-01-12T16:25:34.981Z', '2022-01-12T16:31:20.221Z', '2022-01-12T16:37:08.012Z', '2022-01-12T16:42:21.043Z', '2022-01-12T16:45:03.042Z', '2022-01-13T04:25:34.873Z', '2022-01-13T04:30:27.814Z', '2022-01-13T04:36:10.320Z', '2022-01-13T15:26:33.698Z', '2022-01-14T15:16:26.292Z', '2022-01-14T15:21:38.351Z', '2022-01-14T19:51:59.690Z', '2022-01-16T04:17:27.317Z', '2022-01-16T04:25:13.609Z', '2022-01-16T16:58:38.528Z', '2022-01-16T17:09:46.579Z', '2022-01-16T17:28:21.451Z', '2022-01-16T17:31:03.085Z', '2022-01-16T17:35:09.574Z', '2022-01-16T17:39:57.557Z', '2022-01-17T03:26:34.395Z', '2022-01-17T03:29:16.062Z', '2022-01-17T03:33:22.589Z', '2022-01-17T06:10:43.416Z', '2022-01-17T06:19:04.722Z', '2022-01-17T16:06:32.114Z', '2022-01-17T16:10:24.247Z', '2022-01-17T16:13:54.036Z', '2022-01-17T16:19:36.098Z', '2022-01-17T16:29:31.929Z', '2022-01-17T16:40:15.375Z', '2022-01-17T16:44:21.583Z', '2022-01-17T16:49:09.546Z', '2022-01-17T16:52:44.878Z', '2022-01-17T16:58:30.025Z', '2022-01-17T17:02:40.099Z', '2022-01-17T17:11:27.062Z', '2022-01-17T17:15:58.694Z', '2022-01-17T17:19:29.230Z', '2022-01-17T17:23:26.081Z', '2022-01-17T17:29:11.152Z', '2022-01-17T17:40:03.643Z', '2022-01-17T17:45:16.387Z', '2022-01-17T17:48:07.650Z', '2022-01-17T19:19:37.253Z', '2022-01-17T20:16:24.482Z', '2022-01-18T01:11:46.421Z', '2022-01-18T15:59:02.198Z', '2022-01-18T16:02:54.308Z', '2022-01-18T16:06:22.012Z', '2022-01-18T16:16:25.011Z', '2022-01-18T17:32:09.294Z', '2022-01-18T18:36:34.017Z', '2022-01-18T18:41:36.259Z', '2022-01-18T18:44:58.019Z', '2022-01-18T18:49:34.559Z', '2022-01-18T18:54:12.284Z', '2022-01-18T18:57:06.010Z', '2022-01-18T19:00:34.103Z', '2022-01-18T19:03:34.035Z', '2022-01-18T19:08:09.532Z', '2022-01-18T19:11:26.018Z', '2022-01-18T19:19:22.017Z', '2022-01-19T16:49:00.485Z', '2022-01-19T17:04:16.363Z', '2022-01-19T17:09:09.832Z', '2022-01-19T17:14:52.343Z', '2022-01-19T18:36:12.040Z', '2022-01-19T21:05:56.806Z', '2022-01-19T21:27:21.574Z', '2022-01-20T05:53:29.851Z', '2022-01-20T15:30:55.777Z', '2022-01-20T15:33:38.001Z', '2022-01-20T15:37:43.648Z', '2022-01-20T15:53:34.359Z', '2022-01-20T16:02:19.219Z', '2022-01-20T16:11:16.014Z', '2022-01-20T16:15:47.725Z', '2022-01-20T16:19:18.221Z', '2022-01-20T16:23:15.099Z', '2022-01-20T16:29:00.292Z', '2022-01-21T01:49:08.973Z', '2022-01-21T01:54:01.770Z', '2022-01-21T02:11:34.579Z', '2022-01-21T02:16:08.589Z', '2022-01-21T02:21:53.916Z', '2022-01-21T16:17:06.041Z', '2022-01-21T16:31:52.088Z', '2022-01-21T16:36:44.757Z', '2022-01-21T16:42:27.344Z', '2022-01-21T18:11:55.021Z', '2022-01-21T20:49:07.908Z', '2022-01-21T22:56:11.654Z', '2022-01-22T04:29:32.626Z', '2022-01-22T04:34:05.018Z', '2022-01-22T04:39:47.385Z', '2022-01-22T04:47:44.141Z', '2022-01-22T04:52:03.422Z', '2022-01-22T14:58:55.659Z', '2022-01-22T15:03:44.177Z', '2022-01-22T20:21:18.630Z', '2022-01-23T15:46:57.245Z', '2022-01-23T15:54:57.034Z', '2022-01-23T16:26:19.633Z', '2022-01-23T18:32:36.299Z', '2022-01-23T18:38:22.276Z', '2022-01-23T18:46:36.403Z', '2022-01-23T18:50:34.448Z', '2022-01-23T19:42:04.683Z', '2022-01-23T19:54:18.895Z', '2022-01-23T19:58:38.141Z', '2022-01-23T22:40:54.871Z', '2022-01-24T01:02:21.177Z', '2022-01-24T14:22:50.760Z', '2022-01-24T15:47:24.334Z', '2022-01-24T16:39:53.602Z', '2022-01-24T16:44:26.073Z', '2022-01-24T19:13:28.353Z', '2022-01-24T19:18:27.770Z', '2022-01-24T19:21:01.943Z', '2022-01-24T19:24:54.532Z', '2022-01-24T19:28:36.967Z', '2022-01-24T19:42:05.099Z', '2022-01-24T19:46:10.752Z', '2022-01-24T19:49:36.237Z', '2022-01-24T19:50:09.644Z', '2022-01-25T01:15:25.382Z', '2022-01-25T01:40:38.007Z', '2022-01-25T01:45:27.181Z', '2022-01-25T05:32:18.169Z', '2022-01-25T05:35:12.427Z', '2022-01-25T12:51:15.582Z', '2022-01-25T13:03:21.953Z', '2022-01-25T17:37:59.924Z', '2022-01-25T17:51:31.070Z', '2022-01-25T18:56:23.906Z', '2022-01-25T22:26:36.565Z', '2022-01-25T22:30:35.313Z', '2022-01-26T18:37:30.225Z', '2022-01-26T18:42:19.986Z', '2022-01-26T20:51:44.161Z', '2022-01-26T20:57:15.673Z', '2022-01-26T21:00:58.868Z', '2022-01-26T21:10:36.829Z', '2022-01-26T21:21:41.114Z', '2022-01-26T21:29:37.713Z', '2022-01-28T00:12:22.301Z', '2022-01-28T00:14:16.029Z', '2022-01-28T00:17:03.788Z', '2022-01-28T00:23:43.060Z', '2022-01-28T00:31:18.481Z', '2022-01-28T00:36:45.010Z', '2022-01-28T00:40:51.068Z', '2022-01-28T00:45:40.051Z', '2022-01-28T00:49:15.042Z', '2022-01-28T00:55:00.051Z', '2022-01-28T00:59:10.029Z', '2022-01-28T01:08:02.045Z', '2022-01-28T01:13:47.034Z', '2022-01-28T01:17:57.049Z', '2022-01-28T01:22:44.019Z', '2022-01-28T01:27:16.072Z', '2022-01-28T01:30:46.040Z', '2022-01-28T01:34:43.066Z', '2022-01-28T05:21:20.866Z', '2022-01-28T17:08:10.239Z', '2022-01-28T17:26:03.002Z', '2022-01-28T17:43:19.151Z', '2022-01-28T18:48:35.018Z', '2022-01-28T18:52:40.051Z', '2022-01-28T22:22:47.232Z', '2022-01-29T02:14:39.157Z', '2022-01-29T02:14:43.005Z', '2022-01-29T02:17:20.802Z', '2022-01-29T15:30:26.975Z', '2022-01-29T15:41:08.591Z', '2022-01-29T17:56:01.006Z', '2022-01-29T18:10:54.939Z', '2022-01-29T18:15:47.883Z', '2022-01-29T18:22:02.510Z', '2022-01-30T15:35:32.373Z', '2022-01-30T17:25:34.231Z', '2022-01-31T01:12:31.225Z', '2022-01-31T01:30:22.052Z', '2022-01-31T01:45:08.888Z', '2022-01-31T01:50:01.809Z', '2022-01-31T01:55:44.430Z', '2022-01-31T13:41:08.135Z', '2022-01-31T14:28:51.310Z', '2022-01-31T14:36:12.326Z', '2022-01-31T14:42:28.643Z', '2022-01-31T15:32:50.355Z', '2022-01-31T16:25:40.998Z', '2022-01-31T16:40:27.927Z', '2022-01-31T16:45:20.702Z', '2022-01-31T16:51:03.418Z', '2022-01-31T18:58:10.509Z', '2022-01-31T19:03:03.756Z', '2022-01-31T19:08:46.335Z', '2022-01-31T20:25:21.046Z', '2022-01-31T20:40:07.292Z', '2022-01-31T20:45:00.780Z', '2022-01-31T20:50:43.347Z', '2022-02-01T02:27:06.103Z', '2022-02-02T17:54:44.613Z', '2022-02-02T17:58:50.039Z', '2022-02-02T18:04:17.570Z', '2022-02-02T18:07:53.376Z', '2022-02-02T18:13:38.021Z', '2022-02-02T18:17:48.146Z', '2022-02-02T21:58:06.234Z', '2022-02-02T23:55:51.971Z', '2022-02-03T12:20:13.910Z', '2022-02-03T20:20:36.232Z', '2022-02-03T20:57:48.845Z', '2022-02-04T23:47:30.891Z', '2022-02-05T02:33:00.523Z', '2022-02-05T17:18:12.392Z', '2022-02-05T17:23:25.721Z', '2022-02-05T17:26:08.033Z', '2022-02-05T17:30:14.049Z', '2022-02-05T17:35:02.048Z', '2022-02-05T17:38:38.039Z', '2022-02-05T17:44:23.065Z', '2022-02-05T17:48:33.043Z', '2022-02-05T17:53:20.025Z', '2022-02-05T17:57:52.044Z', '2022-02-05T18:01:22.059Z', '2022-02-05T18:05:19.052Z', '2022-02-05T18:11:04.056Z', '2022-02-05T18:16:52.037Z', '2022-02-05T18:22:04.772Z', '2022-02-05T18:24:48.052Z', '2022-02-05T18:30:44.053Z', '2022-02-05T18:34:36.039Z', '2022-02-05T18:38:05.026Z', '2022-02-05T18:57:49.031Z', '2022-02-05T19:01:30.048Z', '2022-02-05T19:05:46.049Z', '2022-02-05T19:33:28.602Z', '2022-02-05T19:37:34.193Z', '2022-02-06T15:16:48.325Z', '2022-02-06T20:07:09.969Z', '2022-02-06T21:56:33.942Z', '2022-02-07T02:35:03.227Z', '2022-02-07T22:06:46.925Z', '2022-02-10T12:24:23.243Z', '2022-02-10T12:32:37.721Z', '2022-02-10T12:48:28.497Z', '2022-02-10T13:21:55.481Z', '2022-02-11T01:46:39.480Z', '2022-02-11T01:49:20.669Z', '2022-02-11T01:54:23.215Z', '2022-02-11T02:01:11.844Z', '2022-02-11T02:05:59.710Z', '2022-02-11T02:11:57.814Z', '2022-02-11T14:05:12.180Z', '2022-02-11T14:10:04.859Z', '2022-02-11T14:28:41.018Z', '2022-02-11T14:30:38.251Z', '2022-02-11T19:44:29.234Z', '2022-02-11T19:50:47.457Z', '2022-02-12T21:10:13.577Z', '2022-02-13T01:29:16.329Z', '2022-02-13T05:22:09.084Z', '2022-02-13T05:40:53.550Z', '2022-02-13T07:04:54.886Z', '2022-02-13T17:01:20.987Z', '2022-02-13T17:05:05.055Z', '2022-02-13T17:10:47.460Z', '2022-02-13T17:15:59.812Z', '2022-02-13T17:20:00.907Z', '2022-02-13T19:36:25.324Z', '2022-02-13T19:42:07.094Z', '2022-02-14T05:00:35.242Z', '2022-02-14T05:03:25.759Z', '2022-02-14T05:14:42.963Z', '2022-02-14T05:19:35.849Z', '2022-02-14T05:23:52.722Z', '2022-02-14T05:28:04.815Z', '2022-02-14T13:24:34.099Z', '2022-02-14T13:30:23.302Z', '2022-02-14T18:20:12.044Z', '2022-02-14T18:27:53.087Z', '2022-02-14T19:35:18.706Z', '2022-02-14T19:40:21.017Z', '2022-02-14T19:43:43.028Z', '2022-02-14T19:48:19.435Z', '2022-02-14T19:52:58.456Z', '2022-02-14T19:55:50.490Z', '2022-02-14T20:04:16.620Z', '2022-02-14T20:09:18.020Z', '2022-02-14T21:37:42.645Z', '2022-02-14T21:45:28.219Z', '2022-02-14T21:57:14.031Z', '2022-02-14T22:01:52.567Z', '2022-02-14T22:05:03.503Z', '2022-02-14T22:10:17.246Z', '2022-02-15T02:05:24.910Z', '2022-02-15T02:08:48.756Z', '2022-02-15T02:37:46.115Z', '2022-02-15T02:45:32.980Z', '2022-02-15T02:55:24.926Z', '2022-02-15T02:58:43.936Z', '2022-02-15T03:09:07.207Z', '2022-02-15T12:10:25.629Z', '2022-02-15T12:13:36.157Z', '2022-02-15T12:30:31.713Z', '2022-02-15T12:36:44.360Z', '2022-02-15T12:43:09.761Z', '2022-02-15T13:11:50.388Z', '2022-02-15T17:24:28.992Z', '2022-02-15T17:28:28.435Z', '2022-02-15T18:28:54.478Z', '2022-02-15T18:37:52.163Z', '2022-02-15T19:24:50.384Z', '2022-02-16T02:10:30.228Z', '2022-02-16T02:13:39.100Z', '2022-02-16T02:20:27.456Z', '2022-02-16T02:27:47.528Z', '2022-02-16T14:39:11.775Z', '2022-02-16T15:20:48.615Z', '2022-02-16T15:42:53.567Z', '2022-02-16T16:00:43.788Z', '2022-02-16T17:33:05.325Z', '2022-02-16T17:43:33.015Z', '2022-02-16T17:47:26.052Z', '2022-02-16T17:50:55.211Z', '2022-02-16T17:56:37.034Z', '2022-02-16T18:00:18.032Z', '2022-02-16T18:05:57.962Z', '2022-02-16T18:18:48.134Z', '2022-02-16T18:28:28.931Z', '2022-02-16T20:00:16.531Z', '2022-02-16T20:59:48.329Z', '2022-02-16T21:01:42.502Z', '2022-02-16T21:05:24.948Z', '2022-02-16T21:13:06.479Z', '2022-02-16T21:19:45.722Z', '2022-02-16T21:23:02.224Z', '2022-02-16T21:26:24.694Z', '2022-02-16T21:28:29.981Z', '2022-02-16T21:31:17.721Z', '2022-02-16T21:33:47.263Z', '2022-02-16T21:36:35.017Z', '2022-02-16T21:43:13.476Z', '2022-02-16T21:47:30.429Z', '2022-02-16T21:57:02.636Z', '2022-02-16T22:00:55.147Z', '2022-02-16T22:04:31.670Z', '2022-02-16T22:08:40.705Z', '2022-02-16T22:12:12.086Z', '2022-02-16T22:15:00.801Z', '2022-02-16T22:18:51.005Z', '2022-02-17T02:02:49.036Z', '2022-02-17T02:05:52.238Z', '2022-02-17T02:09:35.039Z', '2022-02-17T02:13:18.054Z', '2022-02-17T02:16:49.695Z', '2022-02-17T02:20:42.052Z', '2022-02-17T02:25:26.054Z', '2022-02-17T02:28:22.059Z', '2022-02-17T02:29:14.758Z', '2022-02-17T02:31:59.345Z', '2022-02-17T02:37:30.028Z', '2022-02-17T02:41:30.021Z', '2022-02-17T02:47:12.219Z', '2022-02-17T12:41:12.265Z', '2022-02-17T13:24:24.070Z', '2022-02-17T13:59:55.624Z', '2022-02-17T15:55:49.966Z', '2022-02-17T17:34:02.413Z', '2022-02-17T17:36:42.329Z', '2022-02-17T19:05:18.031Z', '2022-02-17T19:08:05.750Z', '2022-02-17T19:14:44.006Z', '2022-02-17T19:21:26.003Z', '2022-02-17T19:24:19.045Z', '2022-02-17T21:20:41.026Z', '2022-02-17T21:23:34.649Z', '2022-02-17T21:31:31.137Z', '2022-02-17T21:34:59.717Z', '2022-02-17T21:38:00.011Z', '2022-02-17T21:42:36.002Z', '2022-02-17T21:45:52.018Z', '2022-02-17T21:53:47.828Z', '2022-02-17T22:55:03.229Z', '2022-02-17T22:59:47.390Z', '2022-02-17T23:14:37.985Z', '2022-02-18T13:56:29.965Z', '2022-02-18T15:56:56.929Z', '2022-02-18T17:52:34.507Z', '2022-02-19T19:16:24.563Z', '2022-02-19T20:06:01.588Z', '2022-02-19T20:19:57.543Z', '2022-02-19T23:51:52.566Z', '2022-02-20T00:05:18.611Z', '2022-02-20T15:24:43.855Z', '2022-02-20T15:30:47.075Z', '2022-02-20T15:35:04.058Z', '2022-02-20T16:21:48.056Z', '2022-02-20T16:25:32.973Z', '2022-02-20T18:00:20.485Z', '2022-02-20T19:24:32.274Z', '2022-02-20T19:31:48.599Z', '2022-02-20T19:38:51.034Z', '2022-02-20T19:43:53.049Z', '2022-02-20T19:47:15.019Z', '2022-02-20T19:51:51.003Z', '2022-02-20T19:58:49.970Z', '2022-02-20T20:01:43.030Z', '2022-02-20T20:05:57.042Z', '2022-02-20T20:08:57.891Z', '2022-02-20T20:13:34.035Z', '2022-02-20T22:05:46.321Z', '2022-02-20T22:11:21.050Z', '2022-02-20T22:17:40.511Z', '2022-02-20T22:29:44.723Z', '2022-02-21T06:10:47.948Z', '2022-02-21T06:16:30.429Z', '2022-02-21T06:19:13.123Z', '2022-02-21T06:22:49.028Z', '2022-02-21T06:28:34.025Z', '2022-02-21T06:32:44.247Z', '2022-02-21T13:58:48.193Z', '2022-02-21T14:04:30.303Z', '2022-02-21T14:07:13.038Z', '2022-02-21T14:11:18.680Z', '2022-02-21T14:16:07.019Z', '2022-02-21T14:19:42.440Z', '2022-02-21T14:25:32.809Z', '2022-02-21T14:29:42.115Z', '2022-02-21T14:35:39.507Z', '2022-02-21T14:40:11.026Z', '2022-02-21T14:45:59.017Z', '2022-02-21T14:52:21.003Z', '2022-02-21T14:58:06.019Z', '2022-02-21T15:03:54.007Z', '2022-02-21T16:40:21.583Z', '2022-02-21T18:36:04.241Z', '2022-02-21T23:17:22.939Z', '2022-02-22T00:02:21.863Z', '2022-02-22T02:54:23.067Z', '2022-02-22T04:10:14.034Z', '2022-02-22T18:53:21.710Z', '2022-02-22T18:57:27.610Z', '2022-02-22T19:02:15.619Z', '2022-02-22T19:05:51.403Z', '2022-02-22T19:35:34.018Z', '2022-02-22T19:56:34.467Z', '2022-02-23T01:49:54.006Z', '2022-02-23T01:53:59.032Z', '2022-02-23T01:58:48.008Z', '2022-02-23T02:02:23.020Z', '2022-02-23T02:08:08.024Z', '2022-02-23T02:12:18.149Z', '2022-02-23T02:17:06.053Z', '2022-02-23T02:21:37.767Z', '2022-02-23T02:25:08.025Z', '2022-02-23T02:29:05.111Z', '2022-02-23T02:34:50.010Z', '2022-02-23T02:41:07.687Z', '2022-02-23T02:46:19.930Z', '2022-02-23T02:51:14.510Z', '2022-02-23T02:56:02.657Z', '2022-02-23T02:59:38.392Z', '2022-02-23T03:05:22.819Z', '2022-02-23T03:09:33.115Z', '2022-02-23T04:53:32.472Z', '2022-02-23T13:15:56.769Z', '2022-02-23T13:19:29.244Z', '2022-02-23T13:25:11.018Z', '2022-02-23T13:30:52.282Z', '2022-02-23T13:33:33.254Z', '2022-02-23T13:38:20.850Z', '2022-02-23T13:51:10.318Z', '2022-02-23T14:43:32.725Z', '2022-02-23T15:00:22.838Z', '2022-02-23T15:12:41.081Z', '2022-02-23T15:27:09.285Z', '2022-02-23T15:35:34.118Z', '2022-02-23T15:52:06.164Z', '2022-02-23T16:03:22.693Z', '2022-02-23T19:02:44.113Z', '2022-02-23T19:23:49.247Z', '2022-02-23T19:46:57.373Z', '2022-02-23T22:01:36.021Z', '2022-02-23T22:06:49.707Z', '2022-02-23T22:10:19.453Z', '2022-02-23T22:13:56.226Z', '2022-02-23T22:26:12.305Z', '2022-02-24T17:30:10.152Z', '2022-02-24T17:33:39.681Z', '2022-02-24T17:38:53.318Z', '2022-02-24T17:43:25.143Z', '2022-02-24T23:20:05.451Z', '2022-02-25T00:00:21.510Z', '2022-02-25T00:11:35.893Z', '2022-02-25T06:24:57.725Z', '2022-02-25T15:26:46.532Z', '2022-02-27T01:08:02.502Z', '2022-02-27T01:22:52.135Z', '2022-02-27T01:38:05.425Z', '2022-02-27T02:07:35.868Z', '2022-02-27T15:45:00.069Z', '2022-02-27T18:04:04.228Z', '2022-02-27T18:31:39.532Z', '2022-02-27T18:40:34.937Z', '2022-02-28T03:48:21.944Z', '2022-02-28T13:29:52.652Z', '2022-02-28T14:20:54.798Z', '2022-02-28T14:25:58.029Z', '2022-02-28T14:51:30.336Z', '2022-02-28T16:24:01.304Z', '2022-02-28T16:45:45.670Z', '2022-02-28T16:49:56.033Z', '2022-02-28T16:55:41.028Z', '2022-02-28T17:39:27.160Z', '2022-02-28T18:23:34.924Z', '2022-02-28T23:56:58.534Z', '2022-03-01T14:11:31.220Z', '2022-03-01T14:16:04.057Z', '2022-03-01T20:51:28.230Z', '2022-03-02T15:26:27.823Z', '2022-03-02T15:35:19.319Z', '2022-03-02T15:38:09.008Z', '2022-03-02T15:42:15.036Z', '2022-03-02T15:47:03.528Z', '2022-03-02T15:50:39.047Z', '2022-03-02T15:56:24.013Z', '2022-03-02T16:00:34.048Z', '2022-03-02T16:05:21.035Z', '2022-03-02T16:09:53.029Z', '2022-03-02T16:13:23.269Z', '2022-03-02T16:17:20.093Z', '2022-03-02T16:23:05.181Z', '2022-03-02T16:28:53.051Z', '2022-03-02T16:34:06.017Z', '2022-03-02T16:38:38.014Z', '2022-03-02T16:43:43.358Z', '2022-03-02T16:49:09.028Z', '2022-03-02T16:53:56.901Z', '2022-03-02T17:01:57Z', '2022-03-02T17:13:04.375Z', '2022-03-02T17:38:59.827Z', '2022-03-02T18:43:56.006Z', '2022-03-02T18:49:37.962Z', '2022-03-02T18:54:25.025Z', '2022-03-02T18:57:46.017Z', '2022-03-02T19:02:34.041Z', '2022-03-02T19:06:26.117Z', '2022-03-02T19:10:07.039Z', '2022-03-02T20:11:10.408Z', '2022-03-02T22:52:11.424Z', '2022-03-02T22:56:56.959Z', '2022-03-03T13:45:31.175Z', '2022-03-03T19:33:34.381Z', '2022-03-03T23:34:42.120Z', '2022-03-03T23:37:24.028Z', '2022-03-03T23:41:30.037Z', '2022-03-03T23:46:19.032Z', '2022-03-03T23:50:03.007Z', '2022-03-03T23:55:59.049Z', '2022-03-04T00:00:12.044Z', '2022-03-04T00:04:59.022Z', '2022-03-04T00:09:31.020Z', '2022-03-04T00:13:01.050Z', '2022-03-04T00:16:58.038Z', '2022-03-04T00:28:22.673Z', '2022-03-04T00:34:15.010Z', '2022-03-04T00:39:27.987Z', '2022-03-04T19:03:45.479Z', '2022-03-04T23:17:29.104Z', '2022-03-05T05:12:00.027Z', '2022-03-05T16:19:09.306Z', '2022-03-05T22:13:19.363Z', '2022-03-05T22:32:41.591Z', '2022-03-05T22:36:47.631Z', '2022-03-05T22:41:36.006Z', '2022-03-05T22:47:02.350Z', '2022-03-07T01:34:39.152Z', '2022-03-07T05:07:01.875Z', '2022-03-07T05:12:58.421Z', '2022-03-07T05:20:53.230Z', '2022-03-07T05:24:30.758Z', '2022-03-07T05:30:02.003Z', '2022-03-07T05:32:42.585Z', '2022-03-07T05:35:24.507Z', '2022-03-07T05:39:22.366Z', '2022-03-07T14:29:52.001Z', '2022-03-07T14:32:42.693Z', '2022-03-07T14:38:34.981Z', '2022-03-07T14:43:23.057Z', '2022-03-07T14:47:37.171Z', '2022-03-07T14:48:56.056Z', '2022-03-07T14:54:02.036Z', '2022-03-07T14:57:24.004Z', '2022-03-07T15:02:01.037Z', '2022-03-07T15:38:18.074Z', '2022-03-07T15:41:34.969Z', '2022-03-07T15:46:33.812Z', '2022-03-07T15:58:12.776Z', '2022-03-07T17:32:55.339Z', '2022-03-07T23:05:45.173Z', '2022-03-07T23:09:30.624Z', '2022-03-07T23:15:00.769Z', '2022-03-07T23:18:58.274Z', '2022-03-07T23:22:37.235Z', '2022-03-07T23:26:56.530Z', '2022-03-07T23:31:13.731Z', '2022-03-07T23:33:56.150Z', '2022-03-08T00:08:36.890Z', '2022-03-08T02:44:22.738Z', '2022-03-08T02:48:39.739Z', '2022-03-08T03:24:13.189Z', '2022-03-08T03:28:43.997Z', '2022-03-08T15:28:03.023Z', '2022-03-08T15:31:19.758Z', '2022-03-08T15:34:43.009Z', '2022-03-08T15:37:48.038Z', '2022-03-08T15:39:56.770Z', '2022-03-08T15:42:55.384Z', '2022-03-08T15:47:55.903Z', '2022-03-08T15:52:15.099Z', '2022-03-08T15:58:23.026Z', '2022-03-08T16:01:19.019Z', '2022-03-08T16:04:58.871Z', '2022-03-08T16:07:57.039Z', '2022-03-08T18:22:21.160Z', '2022-03-08T19:11:33.486Z', '2022-03-08T20:13:58.692Z', '2022-03-08T20:37:26.373Z', '2022-03-08T21:05:42.386Z', '2022-03-08T21:45:07.780Z', '2022-03-08T21:49:13.565Z', '2022-03-08T21:54:13.729Z', '2022-03-08T21:57:49.276Z', '2022-03-08T22:03:34.118Z', '2022-03-08T22:07:44.870Z', '2022-03-08T22:15:14.761Z', '2022-03-08T22:19:46.753Z', '2022-03-08T22:25:55.797Z', '2022-03-08T23:18:10.875Z', '2022-03-09T01:47:50.120Z', '2022-03-09T01:53:42.287Z', '2022-03-09T14:53:50.219Z', '2022-03-09T17:19:51.937Z', '2022-03-09T19:37:19.343Z', '2022-03-09T19:46:10.445Z', '2022-03-09T19:50:43.783Z', '2022-03-10T22:12:05.353Z', '2022-03-10T22:38:32.448Z', '2022-03-10T23:02:38.320Z', '2022-03-11T21:37:15.440Z', '2022-03-11T21:53:25.054Z', '2022-03-12T21:00:13.977Z', '2022-03-13T01:36:28.893Z', '2022-03-13T01:45:21.312Z', '2022-03-13T15:10:19.250Z', '2022-03-13T18:19:53.064Z', '2022-03-13T18:32:21.062Z', '2022-03-13T18:37:10.025Z', '2022-03-13T18:40:45.064Z', '2022-03-13T20:40:49.035Z', '2022-03-13T21:22:37.929Z', '2022-03-13T21:45:54.862Z', '2022-03-14T00:30:51.727Z', '2022-03-14T00:40:11.415Z', '2022-03-14T00:58:44.074Z', '2022-03-14T02:17:35.383Z', '2022-03-14T11:51:40.278Z', '2022-03-14T14:56:22.240Z', '2022-03-14T15:02:04.398Z', '2022-03-14T15:54:52.076Z', '2022-03-14T17:21:51.113Z', '2022-03-14T21:44:15.308Z', '2022-03-14T22:04:25.080Z', '2022-03-15T11:19:29.540Z', '2022-03-15T11:24:42.929Z', '2022-03-15T11:36:32.801Z', '2022-03-16T02:03:21.056Z', '2022-03-16T02:18:40.291Z', '2022-03-16T17:58:04.553Z', '2022-03-16T22:04:59.164Z', '2022-03-16T22:52:49.922Z', '2022-03-17T12:55:36.615Z', '2022-03-17T16:26:34.911Z', '2022-03-18T13:34:05.040Z', '2022-03-18T15:34:16.062Z', '2022-03-20T05:25:15.365Z', '2022-03-20T20:36:43.540Z', '2022-03-20T20:40:49.020Z', '2022-03-20T23:37:46.770Z', '2022-03-21T11:47:13.943Z', '2022-03-21T11:56:17.026Z', '2022-03-21T13:48:24.836Z', '2022-03-21T14:25:23.447Z', '2022-03-21T15:03:35.928Z', '2022-03-21T18:44:15.055Z', '2022-03-21T19:44:32.992Z', '2022-03-22T03:21:07.458Z', '2022-03-22T04:25:27.053Z', '2022-03-22T04:28:43.690Z', '2022-03-22T04:34:35.416Z', '2022-03-22T14:46:35.947Z', '2022-03-22T16:54:41.130Z', '2022-03-22T18:46:50.954Z', '2022-03-22T21:44:55.006Z', '2022-03-23T14:58:19.069Z', '2022-03-23T19:37:27.230Z', '2022-03-23T20:30:52.715Z', '2022-03-24T03:05:37.570Z']

#%%

parsed_ts = [parser.parse(t).astimezone(est) for t in ts]

num_bins = (parsed_ts[-1] - parsed_ts[0]).days
n, bins, patches = plt.hist(parsed_ts, num_bins)

locs, labels = plt.xticks()
new_labels = []
first_date = parsed_ts[0]

for i, loc in enumerate(locs):
    l = timedelta((loc-locs[0])) + first_date
    lf = f'{l:%b %d}'
    new_labels.append(lf)

plt.xticks(locs, new_labels)
plt.savefig('./top_song_plot.pdf')


# %%
import datetime

t = datetime.datetime.today()
t.year

# %%
