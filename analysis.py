# Joe Nyhan, 26 December 2021; updated 7 January 2021
# Produces a LaTeX generated .pdf and .txt file with top songs, artists, and albums of the day and month

full_summary = True
# full_summary = False
pic_size = "60px"

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
from PIL import Image, ImageDraw, ImageFilter
import matplotlib.pyplot as plt

# user specific details
from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path, sender
from count import get_counts

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = "user-top-read"

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)

def start_of_day_est(dto):
    """
    given a datetime object, returns a datetime object corresponding to the very beginning of the inputted day in EST
    """
    return dto.astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)

def format_artist_names(artists):
    """
    track_info: insert spotify track object; returns formatted string of the artist names
    """
    # artists = track_info["album"]["artists"]
    num_artists = len(artists)
    artist_names = ""

    for i in range(num_artists):
        if i == num_artists-1:
            artist_names += artists[i]
        else: artist_names += artists[i] + ", "

    return artist_names

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

def get_album_artwork(album_id, artwork_url):
    """
    gets image by AlbumID, and stores in local database if not already present
    """
    im_path = f"{home_path}/analysis/images/{album_id}.jpg"
    if not os.path.exists(im_path):
        urlretrieve(artwork_url, im_path)
    return im_path

def get_artist_artwork(artist_id, artwork_url):
    """
    gets image by AlbumID, and stores in local database if not already present
    """
    im_path = f"{home_path}/analysis/artist_images/{artist_id}.jpg"
    if not os.path.exists(im_path):
        temp_path = im_path[0:len(im_path)-4] + "temp.jpg"
        urlretrieve(artwork_url, temp_path)

        # crop image to a square
        im = Image.open(temp_path)
        w, h = im.size
        c = min(w,h)
        cropped_im = im.crop(((w-c) // 2, (h-c) // 2, (w+c) // 2, (h+c) // 2))
        cropped_im.save(im_path)

        os.system(f"rm {temp_path}")

    return im_path

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

def replace_latex_special_characters(s):

    if "&" in s: s = s.replace("&", "\&")
    if "$" in s: s = s.replace("$", "\$")
    if "#" in s: s = s.replace("#", "\#")
    if "%" in s: s = s.replace("%", "\%")

    return s


def count_percent(count, tot):
    ct_pct = count / tot * 100
    if count >= 1000:
        count = str(count)
        count = count[0] + "," + count[1:]
    return f'({count}: {ct_pct:.1f}%) '


def write_block(file, params):
    """
    writes an html block for songs, artists, etc. Place within <div><table></div></table>
    """
    sp_url, pic_url, header, subheader, cl = params
    file.write(f'<tr>\n')
    file.write(f'<td valign="top" width="{pic_size}" height="{pic_size}"><a href="{sp_url}"><img class="{cl}" src="{pic_url}" alt="{header}"></a></td>\n')
    file.write(f'<td valign="middle"><b style="font-size:110%">{header}</b><br>{subheader}</td>\n')
    file.write(f'</tr>\n')


def track_parameters(track, track_db, tot, percent=False):

    id = track['id']
    track_info = track_db[id]

    pic_url = track_info['artwork_url']
    sp_url = track_info['url']
    header = track_info['name']
    subheader = f'({track["count"]}) ' + format_artist_names(track_info['artist_names'])

    return sp_url, pic_url, header, subheader, 'norm'


def album_parameters(album, album_db, tot, percent=False):

    id = album['id']
    album_info = album_db[id]

    pic_url = album_info['artwork_url']
    sp_url = album_info['url']
    header = album_info['name']
    if percent: count = count_percent(album['count'], tot)
    else:       count = f"({album['count']}) "
    subheader = count + format_artist_names(album_info['artist_names'])

    return sp_url, pic_url, header, subheader, 'norm'


def artist_parameters(artist, artist_db, tot, percent=False):

    id = artist['id']
    artist_info = artist_db[id]

    pic_url = artist_info['artwork_url']
    sp_url = artist_info['url']
    header = artist_info['name']
    if percent: count = count_percent(artist['count'], tot)
    else:       count = f"({artist['count']}) "
    subheader = count + format_artist_names(artist_info['genres']).title()

    return sp_url, pic_url, header, subheader, 'circ'


def write_over_list(file, items, items_db, f_params, tot, percent=False):
    file.write('<div><table>')

    for item in items:
        write_block(file, f_params(item, items_db, tot, percent))

    file.write('</div></table>')


def write_header(file, tag, tot=None):
    file.write(f'<h1>{tag}</h1>\n')
    if tot != None:
        file.write(f'<h3>Total songs played: {tot}</h3>\n\n')


def make_formatted_top_songs(songs, file, message, total, track_db, percent=False):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)
    total = str(total)
    if len(total) == 4:
        total = total[0] + "," + total[1:]
    elif len(total) == 5:
        total = total[:2] + "," + total[2:]

    if len(songs) > 10:
        songs = songs[0:10]   

    write_header(file, f"{message}'s Top Songs", total)
    write_over_list(file, songs, track_db, track_parameters, total, percent)

    
def make_formatted_top_artists_albums(file, artists, albums, artist_db, album_db, total, percent=False):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)

    if len(artists) > 5:
        artists = artists[0:5]   
    if len(albums) > 5:
        albums = albums[0:5]   

    write_header(file, "Top Artists")
    write_over_list(file, artists, artist_db, artist_parameters, total, percent)

    write_header(file, "Top Albums")
    write_over_list(file, albums, album_db, album_parameters, total, percent)


def make_user_stamp(file, user_info):
    file.write('<div><table>\n')
    write_block(file, user_info)
    file.write('</div></table>\n')


def make_fullpage_summary(file, counts, dbs, stamp_info, message, pct=False):
    songs, artists, albums, total = counts
    track_db, artist_db, album_db = dbs
    make_formatted_top_songs(songs, file, message, total, track_db)
    make_formatted_top_artists_albums(file, artists, albums, artist_db, album_db, total, percent=pct)


def write_html_header(file):
    file.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Today's Stats!</title>
    <style>

img {
    float: left;
    width: 60px;
    height: 60px;
    padding: 4px;
}

img.norm {
    border-radius: 0%;
}

img.circ {
    border-radius: 50%;
}

h1 {
    font-family: Arial, Helvetica, sans-serif;
}

h3 {
    font-family: Arial, Helvetica, sans-serif;
}

td {
    font-family: Arial, Helvetica, sans-serif;
}
    </style>
</head>
<body>
    """)
    
def write_html_footer(file):
    file.write("""
</body>
</html>
    """)

    

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
    user_pic_path = me["images"][0]["url"]
    user_url = me["external_urls"]["spotify"]

    today_usr_info = user_url, user_pic_path, display_name, today_str, 'circ'
    
    # pdf
    html = open(f"{home_path}/analysis/analysis.html", "w")
    write_html_header(html)
    make_user_stamp(html, today_usr_info)

    if full_summary:
        make_fullpage_summary(html, today_cts, dbs, today_usr_info, "Today")
        make_fullpage_summary(html, month_cts, dbs, today_usr_info, month_str, pct=True)

    else:
        today_track_cts, today_artist_cts, today_album_cts, today_total = today_cts
        month_track_cts, month_artist_cts, month_album_cts, month_total = month_cts
        make_formatted_top_songs(today_track_cts, html, "Today", today_total, track_db)
        make_formatted_top_songs(month_track_cts, html, month_str, month_total, track_db)

    write_html_footer(html)
    html.close()

    # write updated database
    dbs = track_db, artist_db, album_db
    with open(f"{home_path}/data/{my}-database.txt","w") as output:
        output.write(json.dumps(dbs))

if __name__ == "__main__":
    main()
