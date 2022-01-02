# Joe Nyhan, 26 December 2021
# Produces a LaTeX generated .pdf and .txt file with top songs of the day and month
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

redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)

yesterday = False
otherday = ""
if len(sys.argv) == 2:
        if sys.argv[1] == "y": yesterday = True
        else: 
            # otherday = sys.argv[1]
            # TODO: implement a way to standardize adding any date to allow for an analysis for any date
            pass

#%% 

# ========== USEFUL FUNCTIONS

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

def make_image_circular(input_path, output_path):
    img = Image.open(input_path)
    height,width = img.size
    lum_img = Image.new('L', [height,width] , 0)

    draw = ImageDraw.Draw(lum_img)
    draw.pieslice([(0,0), (height,width)], 0, 360, fill = 255, outline = "white")
    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)
    final_img_arr = np.dstack((img_arr,lum_img_arr))

    img = Image.fromarray(final_img_arr)
    img.save(output_path)

def make_counts(df, start, end):
    """
    Given a dataframe, a starting date and an ending date (both datetime objects), return a data frame of the value counts for song ids
    """
    songs = pd.DataFrame(columns=["ID","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > start and parsed < end:
            songs = songs.append(df.iloc[i,:])
    
    return songs["ID"].value_counts()

def get_song_info(db, id):
    if not id in db:
        track = sp.track(id)
        artist_ids = []
        artist_names = []
        for artist in track["album"]["artists"]:
            artist_ids.append(artist["id"])
            artist_names.append(artist["name"])
        name = track["name"]
        pic_url = track["album"]["images"][1]["url"]
        sp_url = track["external_urls"]["spotify"]
        album_id = track["album"]["id"]
        album_name = track["album"]["name"]

        # adds this entry to the database for future reference
        db[id] = {"name": name,
            "ArtistIDs": artist_ids,
            "ArtistNames": artist_names,
            "AlbumID": album_id,
            "AlbumName": album_name,
            "PicURL": pic_url,
            "SpotifyURL": sp_url
        }

    return db[id]
    
def get_image(track_info):
    """
    gets image by AlbumID, and stores in local database if not already present
    """
    album_id = track_info["AlbumID"]
    im_path = f"{home_path}/analysis/images/{album_id}.jpg"
    if not os.path.exists(im_path):
        urlretrieve(track_info["PicURL"], im_path)
    return im_path

def sort_songs(counts, db):

    keys = counts.keys()
    if len(keys) > 25: keys = keys[0:25] # only sort first 25 keys

    sorted = []
    for key in keys:
        name = get_song_info(db, key)["name"]
        # name = sp.track(key)["name"]
        sorted.append({"name": name, "ID": key, "count": counts[key]})

    def sort_by_name(d): return -d["count"], d["name"]

    sorted.sort(key=sort_by_name)
    return sorted


def make_top_songs(songs, file, message, total, db):
    """
    prints out the top songs for a given pd.series containing counts
    """
    if len(songs) > 10: songs = songs[0:10]

    file.write(message + "\n")

    for song in songs:
        id = song["ID"]
        track_info = get_song_info(db, id)
        # track_info = sp.track(id)
        name = song["name"]
        count = song["count"]

        artist_names = format_artist_names(track_info["ArtistNames"])
    
        file.write(f"{count:3d}  {name}, by {artist_names}\n")
    
    file.write(f"Total songs played: {total}\n")

def make_formatted_top_songs(songs, file, message, total, db):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)
    total = str(total)
    if len(total) == 4:
        total = total[0] + "," + total[1:]

    ltf = False

    if len(songs) < 5:
        ltf = True

    if len(songs) > 10:
        songs = songs[0:10]   

    file.write("\\noindent\\LARGE{" + f"{message}" + "}\\hfill \\large{" + f"Total songs played: {total}" + "}\\\\[10pt]\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")

    def write(song):
        
        id = song["ID"]
        # get information to write
        # track_info = sp.track(id)
        track_info = get_song_info(db, id)
        # urlretrieve(track_info["PicURL"], f"{home_path}/analysis/{t}{i}.jpg")
        pic_path = get_image(track_info)
        name = track_info["name"]
        count = f"({song['count']}) "
        artist_names = count + format_artist_names(track_info["ArtistNames"])
        sp_url = track_info["SpotifyURL"]

        # replace latex special characters
        if "&" in name: name = name.replace("&", "\&")
        if "$" in name: name = name.replace("$", "\$")
        if "#" in name: name = name.replace("#", "\#")
        if "&" in artist_names: artist_names = artist_names.replace("&", "\&")
        if "$" in artist_names: artist_names = artist_names.replace("$", "\$")
        if "#" in artist_names: artist_names = artist_names.replace("#", "\#")

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\href{" + sp_url + "}{\\includegraphics[width = \\textwidth]{" + pic_path + "}}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{\\truncate{\\textwidth}{" + name + "} }\\\\[2pt]\n")
        file.write("\\footnotesize \\truncate{\\textwidth}{" + artist_names + "}\n")
        file.write("\\end{minipage}\\\\[5pt]\n")
        file.write("\n")

    upp = 5
    if len(songs) < upp: upp = len(songs)
    for i in range(upp):
        write(songs[i])

    file.write("\\end{minipage}\\hfill%\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    
    if not ltf:
        upp = 10 
        if len(songs) < upp: upp = len(songs)
        for i in range(5,upp):
            write(songs[i])
    
    file.write("\\end{minipage}\n")
    file.write("\\vspace{15pt}\n\n")



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
songs = pd.read_csv(f"{home_path}/data/{my}-songlist.txt")

# get local song database
if os.path.exists(f"{home_path}/data/{my}-database.txt"):
    with open(f"{home_path}/data/{my}-database.txt","r") as f:
        db = json.loads(f.read())
else: db = {}

today_cts = make_counts(songs, day, eod)
today_topsongs = sort_songs(today_cts, db)
today_total = today_cts.sum()

month_cts = make_counts(songs, month, eod)
month_topsongs = sort_songs(month_cts, db)
month_total = month_cts.sum()

# ========== write to file

# user information
me = sp.current_user()
display_name = me["display_name"]


# textfile
txt = open(f"{home_path}/analysis/analysis.txt", "w")

make_top_songs(today_topsongs, txt, "TODAY'S TOP SONGS", today_total, db)
txt.write("\n")
make_top_songs(month_topsongs, txt, f"{month_str.upper()}'S TOP SONGS", month_total, db)

txt.write(f"\n{display_name}, {today_str}")

txt.close()


# pdf
pdf = open(f"{home_path}/analysis/part.tex", "w")

make_formatted_top_songs(today_topsongs, pdf, "Today's Top Songs", today_total, db)
make_formatted_top_songs(month_topsongs, pdf, f"{month_str}'s Top Songs", month_total, db)

# ========== USER INFO AT BOTTOM OF PDF

# get profile photo
urlretrieve(me["images"][0]["url"],f"{home_path}/analysis/pp.jpg")
# make image a circle
make_image_circular(f"{home_path}/analysis/pp.jpg",f"{home_path}/analysis/circpp.png")

# get user url
user_url = me["external_urls"]["spotify"]

# print image, date, user name to file
pdf.write("\\vfill\\raggedleft\n")
pdf.write("\\begin{minipage}{.47\\textwidth}\n")
pdf.write("\\raggedleft")
pdf.write("\\begin{minipage}{.75\\textwidth}\n")
pdf.write("\\raggedleft\\large \\href{"+ user_url + "}{\\textbf{" + display_name +  "}}\\\\[2pt]\n")
# pdf.write("\\raggedleft\\large " + f"{display_name}" +  "\\\\[2pt]\n")
pdf.write(f"\\normalsize {today_str}")
pdf.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
pdf.write("\\begin{minipage}{.2\\textwidth}\n")
pdf.write("\\includegraphics[width = \\textwidth]{" + f"{home_path}" + "/analysis/circpp.png}\n")
pdf.write("\\end{minipage}\\end{minipage}\n")

pdf.close()

# write updated database
with open(f"{home_path}/data/{my}-database.txt","w") as output:
    output.write(json.dumps(db))

# compile and delete auxillary files
os.system(f"{pdflatex_path} -output-directory={home_path}/analysis {home_path}/analysis/analysis.tex > {home_path}/analysis/pdflatex_output.txt")
# delte auxillary files
os.system(f"rm {home_path}/analysis/analysis.aux")
os.system(f"rm {home_path}/analysis/analysis.log")
os.system(f"rm {home_path}/analysis/analysis.out")
os.system(f"rm {home_path}/analysis/*.jpg")
os.system(f"rm {home_path}/analysis/*.png")
os.system(f"rm {home_path}/analysis/part.tex")
os.system(f"rm {home_path}/analysis/pdflatex_output.txt")
