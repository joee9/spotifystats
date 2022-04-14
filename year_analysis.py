# Joe Nyhan, 31 December 2021; updated 7 January 2021
# Creates a LaTeX generated yearly summary; see yearly_sum_example.pdf

# TODO: update to write monthly databases

#%%

# spotify libraries
import spotipy.util as util
import spotipy

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
import numpy as np
from urllib.request import urlretrieve
from PIL import Image, ImageDraw

# user specific details
from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path, sender
from analysis import make_fullpage_summary, make_formatted_top_songs, start_of_day_est, make_user_stamp, write_html_header, write_html_footer
from count import get_counts

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = "user-top-read"

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)


def main():

    sp = get_auth()

    yyyy = 2022
    if len(sys.argv) == 2:
            yyyy = int(sys.argv[1])

    # ========== USER INFORMATION
    me = sp.current_user()
    display_name = me["display_name"]
    user_pic_path = me["images"][0]["url"]
    user_url = me["external_urls"]["spotify"]

    usr_info = user_url, user_pic_path, display_name, f'Yearly Recap: {yyyy}', 'circ'


    # ========== CREATE DATA FRAMES FOR EACH MONTH

    all_songs = pd.DataFrame(columns=["ID","Timestamp"])
    large_track_db = {}
    large_artist_db = {}
    large_album_db = {}
    months = []

    for mm in range(1,13):

        path = f"{home_path}/data/{yyyy}-{mm:02d}"
        if os.path.exists(f"{path}-songlist.txt"):
            df = pd.read_csv(f"{path}-songlist.txt")
            all_songs = pd.concat([all_songs,df])
            months.append(mm)
        
        if os.path.exists(f"{path}-database.txt"):
            with open(f"{path}-database.txt","r") as f:
                dbs = json.loads(f.read())
                track_db, artist_db, album_db = dbs
                large_track_db.update(track_db)
                large_artist_db.update(artist_db)
                large_album_db.update(album_db)
    
    all_dbs = large_track_db, large_artist_db, large_album_db

    html = open(f"{home_path}/analysis/year_analysis.html", "w")
    write_html_header(html)

    make_user_stamp(html, usr_info)

    # do yearly stats first
    year_cts = get_counts(sp, all_songs, all_dbs)

    make_fullpage_summary(html, year_cts, all_dbs, usr_info, str(yyyy), pct=True)

    # monthly top songs
    for i in range(len(months)):
        mm = months[i]
        tag = datetime.strftime(datetime.today().replace(month =mm, day=1), "%B")
        path = f"{home_path}/data/{yyyy}-{mm:02d}"
        df = pd.read_csv(f"{path}-songlist.txt")
        pic_str = f"m{i}-"

        m_song_cts, m_artist_cts, m_album_cts, m_total = get_counts(sp, df, all_dbs)

        make_formatted_top_songs(m_song_cts, html, tag, m_total, large_track_db)
    

    write_html_footer(html)
    html.close()

if __name__ == "__main__":
    main()
