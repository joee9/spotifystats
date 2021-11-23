#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime
import pytz
est = pytz.timezone("America/New_York")
utc = pytz.timezone("UTC")
from dateutil import parser
from os.path import exists

from secrets import username, client_id, client_secret, home_path

my = datetime.strftime(datetime.today().astimezone(est), "%m-%Y")
path = f"{home_path}/data/{my}-recentlyplayed.txt"

redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

if exists(path):
    new_month = False
    df = pd.read_csv(path)
    # df.drop(df.tail(5).index,inplace=True) # drop last five songs; just in case spotify took a while to update; basically, start at an earlier time, but don't add a song more than once
    latest_time_stamp = df.tail(1).to_numpy()[0][1]
    latest_time = parser.parse(latest_time_stamp)

else:
    new_month = True
    df = pd.DataFrame(columns = ["URI", "Timestamp"])
    # latest_time = datetime.today().replace(day=1, second=0, minute=0, hour=0, microsecond=0).astimezone(utc) # beginning of month
    latest_time = datetime.today().astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)
    # latest_time = datetime.today().astimezone(est).replace(second=0,minute=0,hour=0,microsecond=1)
    print(latest_time)
    # latest_time.replace()

#%%

lim = 50

recently_played = sp.current_user_recently_played(limit=lim)

# find the time that the oldest track in recently_played was played
oldest_rp_ts = recently_played["items"][lim-1]["played_at"]
oldest_rp_time = parser.parse(oldest_rp_ts)

if oldest_rp_time > latest_time: # all rp tracks are more recent than the df
    idx = 1 # add all songs to the tail of df

# determine all of the 
elif not new_month:
    n = -1
    # determine the times in the df that are after rp
    for i in range(len(df)):
        curr_ts = parser.parse(df.iloc[i,1])
        if curr_ts >= oldest_rp_time:
            n = (len(df)-1) - i + 1
            break

#%%
    if n != -1:
        # delete all tracks that are newer than last rp track
        df.drop(df.tail(n).index,inplace=True)
    idx = 1 # add all rp songs to the tail of df

#%%

else:
    # determine which songs from rp are from this month and add to df
    # only for new month
    for i in range(1,lim+1):
        track_ts = recently_played["items"][lim - i]["played_at"]
        parsed_track_ts = parser.parse(track_ts)
        if parsed_track_ts > latest_time:
            idx = i
            break

# add appropriate songs to df
for i in range(idx, lim+1):

    track_uri = recently_played["items"][lim - i]["track"]["uri"]
    track_ts = recently_played["items"][lim - i]["played_at"]

    df = df.append({
        "URI": track_uri,
        "Timestamp": track_ts
    }, ignore_index=True)

    
df.to_csv(path, index=False)



# for i in range(1, lim+1):

#     track_name = recently_played["items"][lim - i]["track"]["name"]
#     track_uri = recently_played["items"][lim - i]["track"]["uri"]

#     time_stamp = recently_played["items"][lim - i]["played_at"]
#     time = parser.isoparse(time_stamp)
#     time_est = time.astimezone(est)
#     time_print = datetime.strftime(time_est, "%c")

#     if latest_time < time:
#         print(f"{track_name:50s} on {time_print}")
#         df = df.append({
#             "URI": track_uri,
#             "Timestamp": time_stamp
#         }, ignore_index=True)


# # %%
# # timerange = "long_term"
# timerange = "medium_term"
# # timerange = "short_term"
# top_tracks = sp.current_user_top_tracks(time_range=f"{timerange}", limit=50)
# n = top_tracks["total"]

# for i in range(0,n):
# # if True:
#     s = top_tracks["items"][i]["name"]
#     print(f"{i+1}. {s}")


# # %%

# recently_played = sp.current_user_recently_played(limit=50)

# id = recently_played["items"][0]["track"]["uri"]

# track = sp.track(id)
# %%
