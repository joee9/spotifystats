# Joe Nyhan, 6 December 2021
# When run, this file writes recently played songs to ./data/%m-%Y-recentlyplayed.txt

# spotify libraries
import spotipy.util as util # for getting authorization
import spotipy              # for getting tracks, etc.

# time related packages
from datetime import datetime, timedelta
import pytz
est = pytz.timezone("America/New_York")
utc = pytz.timezone("UTC")
from dateutil import parser

# os related
from os.path import exists
import sys

# for analysis
import pandas as pd
# client information
from secrets import username, client_id, client_secret, home_path

# TODO: implement code that will add all remaining songs from last month to last months rp file automatically

my = datetime.strftime(datetime.today().astimezone(est), "%m-%Y") # month year; for file paths
path = f"{home_path}/data/{my}-songlist.txt"


# get authorization token
redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"
token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

# create spotify object for getting information
sp = spotipy.Spotify(auth=token)

if exists(path): # if monthly file already exists
    new_month = False
    df = pd.read_csv(path)
    if len(df) == 0: # file created, but no songs yet; a new month
        new_month = True
        latest_time = datetime.today().astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)
    else:
        latest_time_stamp = df.tail(1).to_numpy()[0][1]
        latest_time = parser.parse(latest_time_stamp)

else:
    new_month = True
    df = pd.DataFrame(columns = ["ID", "Timestamp"])
    latest_time = datetime.today().astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)

# get recently played songs
lim = 50
recently_played = sp.current_user_recently_played(limit=lim)

# find the time that the oldest track in recently_played was played 
oldest_rp_ts = recently_played["items"][lim-1]["played_at"]
oldest_rp_time = parser.parse(oldest_rp_ts)

# earliest time that can be in this month; beginning of first day
earliest_time = datetime.today().astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)

if oldest_rp_time > latest_time: # all rp tracks are more recent than the df
    idx = 1 # add all songs to the tail of df

# deterime all times in df that are also included in rp and remove them
elif not new_month:
    n = -1
    for i in range(len(df)):
        curr_ts = parser.parse(df.iloc[i,1])
        if curr_ts >= oldest_rp_time:
            n = (len(df)-1) - i + 1
            break
    if n != -1:
        # delete all tracks that are newer than last rp track
        df.drop(df.tail(n).index,inplace=True)
    idx = 1 # add all rp songs to the tail of df


else:
    # determine which songs from rp are from this month and add to df
    # only for new month
    idx = lim + 1
    for i in range(1,lim+1):
        track_ts = recently_played["items"][lim - i]["played_at"]
        parsed_track_ts = parser.parse(track_ts)
        if parsed_track_ts > latest_time:
            idx = i
            break

# add appropriate songs to df
for i in range(idx, lim+1):

    track_id = recently_played["items"][lim - i]["track"]["id"]
    track_ts = recently_played["items"][lim - i]["played_at"]

    # only add if in this month
    if parser.parse(track_ts) > earliest_time:
        df = df.append({
            "ID": track_id,
            "Timestamp": track_ts
        }, ignore_index=True)

    
# write back to df
df.to_csv(path, index=False)