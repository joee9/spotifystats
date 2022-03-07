# Joe Nyhan, 26 December 2021; updated 7 January 2021
# Produces a LaTeX generated .pdf and .txt file with top songs, artists, and albums of the day and month

full_summary = True
# full_summary = False

#%%

from auth import get_auth
from latex import *

# time related
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser

#system related
import os
import sys
import json

# misc
import pandas as pd

# user specific details
from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path, sender
from count import get_counts

def start_of_day_est(dto):
    """
    given a datetime object, returns a datetime object corresponding to the very beginning of the inputted day in EST
    """
    return dto.astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)

def make_df_range(df, start, end):
    """
    Given a dataframe, a starting date and an ending date (both datetime objects), return a data frame of the value counts for song ids
    """
    songs = pd.DataFrame(columns=["ID","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > start and parsed < end:
            songs = songs.append(df.iloc[i,:])
    
    return songs

# for text files
def make_top_songs(counts, file, message, db): 
    """
    prints out the top songs for a given pd.series containing counts
    """
    song_cts, artists, albums, total = counts
    if len(song_cts) > 10: song_cts = song_cts[0:10]

    file.write(message + "\n")

    for song in song_cts:
        id = song['id']
        track_info = db[id]
        name = song['name']
        count = song['count']

        artist_names = format_artist_names(track_info['artist_names'])
    
        file.write(f"{count:3d}  {name}, by {artist_names}\n")
    
    file.write(f"Total songs played: {total}\n")

def main():
    sp = get_auth()

    yesterday = False
    otherday = ""
    if len(sys.argv) == 2:
        if sys.argv[1] == "y": yesterday = True
        else: 
            otherday = sys.argv[1]
            # TODO: implement a way to standardize adding any date to allow for an analysis for any date
            pass

    # ========== MAKE DATAFRAMES, COUNTS, ETC.

    # get datetime of "today", the day in question
    day = start_of_day_est(datetime.today())

    if yesterday: 
        day = day - timedelta(days = 1)
    elif otherday != "": 
        day = start_of_day_est(parser.parse(otherday))

    # end of day is one day later than the day object
    eod = day + timedelta(days=1)

    # get DTO of the beginning of the current month
    m = int(datetime.strftime(day, "%m"))
    month = day.replace(month = m, day = 1)

    # get a string for the date, e.g. 12-2021
    my = datetime.strftime(day, "%Y-%m")
    month_str = datetime.strftime(month, "%B")
    today_str = datetime.strftime(day,"%B %d, %Y")

    # get relevant series and dfs
    songlist = pd.read_csv(f"{home_path}/data/{my}-songlist.txt")

    # get local song database
    if os.path.exists(f"{home_path}/data/{my}-database.txt"):
        with open(f"{home_path}/data/{my}-database.txt","r") as f:
            dbs = json.loads(f.read()) # track_db, artist_db, album_db
    else: dbs = {},{},{}


    today_df = make_df_range(songlist, day, eod)
    today_cts = get_counts(sp, today_df, dbs)

    month_df = make_df_range(songlist, month, eod)
    month_cts = get_counts(sp, month_df, dbs)

    track_db, artist_db, album_db = dbs

    # ========== WRITE TO FILE

    # user information
    me = sp.current_user()
    display_name = me["display_name"]
    # get profile photo
    pp_path = f'{home_path}/analysis/pp.png'
    urlretrieve(me["images"][0]["url"],pp_path)
    make_image_circular(pp_path,pp_path)
    # get user url
    user_url = me["external_urls"]["spotify"]
    today_usr_info = display_name, user_url, pp_path, today_str


    # textfile
    txt = open(f"{home_path}/analysis/analysis.txt", "w")

    make_top_songs(today_cts, txt, "TODAY'S TOP SONGS", track_db)
    txt.write("\n")
    make_top_songs(month_cts, txt, f"{month_str.upper()}'S TOP SONGS", track_db)

    txt.write(f"\n{display_name}, {today_str}")

    txt.close()


    # pdf
    pdf = open(f"{home_path}/analysis/part.tex", "w")

    if full_summary:
        make_fullpage_summary(pdf, today_cts, dbs, today_usr_info, "Today")
        make_fullpage_summary(pdf, month_cts, dbs, today_usr_info, month_str, pct=True)
    else:
        today_track_cts, today_artist_cts, today_album_cts, today_total = today_cts
        month_track_cts, month_artist_cts, month_album_cts, month_total = month_cts
        make_formatted_top_songs(today_track_cts, pdf, "Today", today_total, track_db)
        make_formatted_top_songs(month_track_cts, pdf, month_str, month_total, track_db)
        make_user_stamp(pdf, today_usr_info)

    pdf.close()

    # write updated database
    dbs = track_db, artist_db, album_db
    with open(f"{home_path}/data/{my}-database.txt","w") as output:
        output.write(json.dumps(dbs))

    # compile and delete auxillary files
    os.system(f"{pdflatex_path} -output-directory={home_path}/analysis {home_path}/analysis/analysis.tex > {home_path}/analysis/pdflatex_output.txt")
    # delte auxillary files
    os.system(f"rm {home_path}/analysis/analysis.aux")
    os.system(f"rm {home_path}/analysis/analysis.log")
    os.system(f"rm {home_path}/analysis/analysis.out")
    os.system(f"rm {home_path}/analysis/*.png")
    os.system(f"rm {home_path}/analysis/part.tex")
    os.system(f"rm {home_path}/analysis/pdflatex_output.txt")

if __name__ == "__main__":
    main()
