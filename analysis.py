#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
from dateutil.tz import tzutc
import os
import sys

from secrets import username, client_id, client_secret, home_path, python_path

path = home_path
python = python_path

os.system(f"{python} {path}/get_rp.py >> {path}/newsongs.txt")
os.system(f"rm {path}/newsongs.txt")

# if len(sys.argv) == 0 or len(sys.argv) == 1:
#     mode = "top_10"
mode = "top_10"
tf = "dm"

yesterday = False
if len(sys.argv) == 2 and sys.argv[1] == "y":
    yesterday = True

# if len(sys.argv) == 2:
#     mode = sys.argv[1]
# elif len(sys.argv) == 3:
#     mode = sys.argv[1]
#     tf = sys.argv[2]
# elif len(sys.argv) > 3:
#     print("Too many arguments!")
#     exit()
# mode = "top_10"

if mode == "top_10" or mode == "all":
    pass
else:
    print("Incorrect Mode!")
    exit()

if tf in ["today", "month", "year", "dm"]:
    pass
else:
    print("Incorrect TimeFrame!")
    exit()

redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

## useful methods

def format_artist_names(track_info):
    artists = track_info["album"]["artists"]
    num_artists = len(artists)
    artist_names = ""

    if num_artists == 1:
        artist_names = artists[0]["name"]
    elif num_artists == 2:
        artist_names = artists[0]["name"] + " and " + artists[1]["name"]
    else:
        for i in range(num_artists):
            if i == num_artists-1:
                artist_names += f"and {artists[i]['name']}"
            else: artist_names += f"{artists[i]['name']}, "

    return artist_names

def top_songs(counts, mode):
    keys = counts.keys()

    if len(keys) > 25: keys = keys[0:25]

    sorted = []
    for key in keys:
        name = sp.track(key)["name"]
        sorted.append({"name": name, "URI": key, "count": counts[key]})

    def sort_by_name(d): return -d["count"], d["name"]

    sorted.sort(key=sort_by_name)

    sorted_keys = []
    for entry in sorted:
        sorted_keys.append(entry["URI"])
    
    keys = sorted_keys

    if mode == "top_10" and len(keys) > 10:
        keys = keys[0:10]

    for id in keys:
        track_info = sp.track(id)
        name = track_info["name"]
        count = counts[id]
        artist_names = format_artist_names(track_info)
    
        print(f"{count:3d}  {name}, by {artist_names}")

def make_counts(df,date,end):
    songs = pd.DataFrame(columns=["URI","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > date and parsed < end:
            songs = songs.append(df.iloc[i,:])
    
    return songs["URI"].value_counts()

dates = []
messages = []
tags = []

day_cutoff = datetime.today().astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)
month_cutoff = datetime.today().astimezone(est).replace(day=1, second=0, minute=0, hour=0, microsecond=0)
end = datetime.today().astimezone(est)

if yesterday:
    
    day_cutoff = day_cutoff - timedelta(days=1)

    m = int(datetime.strftime(day_cutoff,"%m"))
    month_cutoff = datetime.today().astimezone(est).replace(month=m, day=1, second=0, minute=0, hour=0, microsecond=0)
    
    end = datetime.today().astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)

today_str = datetime.strftime(day_cutoff,"%B %d, %Y")

my = datetime.strftime(day_cutoff, "%m-%Y")
df = pd.read_csv(f"{path}/data/{my}-recentlyplayed.txt")

if tf == "today":
    messages.append("TODAY'S TOP SONGS")
    dates.append(day_cutoff)
    tags.append("today")

elif tf == "month":
    messages.append("THIS MONTH'S TOP SONGS")
    dates.append(month_cutoff)
    tags.append("this month")

elif tf == "dm":
    messages.append("TODAY'S TOP SONGS")
    dates.append(day_cutoff)
    tags.append("today")
    messages.append("THIS MONTH'S TOP SONGS")
    dates.append(month_cutoff)
    tags.append("this month")
    

for i in range(len(dates)):
    date = dates[i]
    tag = tags[i]
    print(messages[i])
    print(f"###  SONG")
    counts = make_counts(df, date, end)
    total = counts.sum()
    top_songs(counts, mode)
    print(f"Total songs played {tag}: {total}")
    print(f"")




# time = parser.isoparse(time_stamp)
# time_est = time.astimezone(est)
# time_print = datetime.strftime(time_est, "%c")
