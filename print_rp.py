import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
import os
import sys
from urllib.request import urlretrieve

from secrets import username, client_id, client_secret, home_path, python_path

path = home_path
python = python_path

os.system(f"{python} {path}/get_rp.py >> {path}/newsongs.txt")
os.system(f"rm {path}/newsongs.txt")

name_lim = 35
artist_lim = 30

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

    if len(artist_names) > artist_lim:
        artist_names = artist_names[0:artist_lim-3] + "..."

    return artist_names

today = datetime.today().astimezone(est)
my = datetime.strftime(today,"%m-%Y")


if len(sys.argv) == 2:
    num = int(sys.argv[1])
else:
    print("Incorrect arguments! Please try again!")
    exit()


redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

df = pd.read_csv(f"{home_path}/data/{my}-recentlyplayed.txt")

n = len(df)
for i in range(num):
    id = df["URI"].iloc[n-1-i]
    ts = df["Timestamp"].iloc[n-1-i]

    t_id = sp.track(id)
    name = t_id["name"]

    if len(name) > name_lim:
        name = name[0:name_lim-3] + "..."

    artist_names = format_artist_names(t_id)
    time = datetime.strftime(parser.parse(ts).astimezone(est), "%c")

    print(f"{name:36s} {artist_names:31s} @ {time}")

