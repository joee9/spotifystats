# Joe Nyhan, 6 December 2021; updated 5 November 2022
# When run, this file writes recently played songs to ./data/%m-%Y-recentlyplayed.txt
#%%

import pandas as pd
from os.path import exists

# time related packages
from datetime import datetime, timedelta
import pytz
est = pytz.timezone("America/New_York")
utc = pytz.timezone("UTC")
from dateutil import parser

from general import get_auth

from secrets import home


def get_rp_songs_on_day(sp, day):

    my = datetime.strftime(day, "%Y-%m") # month year; for file paths
    path = f"{home}/data/{my}-songlist.txt"

    # beginning of very next day; lastest timestamp that could be added
    latest_time = (day + timedelta(days = 1)).replace(hour=0,second=0,minute=0,microsecond=0)

    if exists(path): # if monthly file already exists
        new_month = False
        df = pd.read_csv(path)
        if len(df) == 0: # file created, but no songs yet; a new month
            new_month = True
            most_recent_time = day.astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)
        else:
            most_recent_timestamp = df.tail(1).to_numpy()[0][1]
            most_recent_time = parser.parse(most_recent_timestamp)

    else:
        new_month = True
        df = pd.DataFrame(columns = ["ID", "Timestamp"])
        most_recent_time = day.astimezone(est).replace(day=1,second=0,minute=0,hour=0,microsecond=1)

    # get recently played songs
    lim = 40
    recently_played = sp.current_user_recently_played(limit=lim)

    # find the time that the oldest track in recently_played was played 
    oldest_rp_ts = recently_played["items"][lim-1]["played_at"]
    oldest_rp_time = parser.parse(oldest_rp_ts)

    # earliest time that can be in this month; beginning of first day
    earliest_time = day.replace(day=1,second=0,minute=0,hour=0,microsecond=1)

    if oldest_rp_time > most_recent_time: # all rp tracks are more recent than the df
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
            if parsed_track_ts > most_recent_time:
                idx = i
                break

    # add appropriate songs to df
    for i in range(idx, lim+1):

        track_id = recently_played["items"][lim - i]["track"]["id"]
        track_ts = recently_played["items"][lim - i]["played_at"]

        # only add if in this month
        track_time = parser.parse(track_ts)
        if track_time >= earliest_time and track_time < latest_time:
            df = df.append({
                "ID": track_id,
                "Timestamp": track_ts
            }, ignore_index=True)

        
    # write back to df
    df.to_csv(path, index=False)


def get_rp(sp):

    # ========== GET DAYS TO RUN (usually just today)
    today = datetime.today().astimezone(est)
    yesterday = today - timedelta(days=1)

    t_str = datetime.strftime(today,"%Y-%m")
    y_str = datetime.strftime(yesterday,"%Y-%m")

    days_to_run = [today]

    if t_str != y_str: # today and yesterday were in different months
        days_to_run.append(yesterday)
    # run necessary days
    for day in days_to_run:
        get_rp_songs_on_day(sp, day)


def main():
    sp = get_auth()
    get_rp(sp)


if __name__ == "__main__":
    main()
