# Joe Nyhan, 31 December 2021
# Prints out top songs from each month, as well as the top songs from the current year

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

def get_auth():
    redirect_uri = 'http://localhost:7777/callback'
    # scope = 'user-read-recently-played'
    scope = "user-top-read"

    token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

    return spotipy.Spotify(auth=token)


# ========== USEFUL FUNCTIONS

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

def get_song_info(sp, db, id):
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
    album_id = track_info["AlbumID"]
    im_path = f"{home_path}/analysis/images/{album_id}.jpg"
    if not os.path.exists(im_path):
        urlretrieve(track_info["PicURL"], im_path)
    return im_path
    

def sort_songs(sp, counts, db, num = 25):

    keys = counts.keys()
    if len(keys) > num: keys = keys[0:num] # only sort first 25 keys

    sorted = []
    for key in keys:
        name = get_song_info(sp, db, key)["name"]
        # name = sp.track(key)["name"]
        sorted.append({"name": name, "ID": key, "count": counts[key]})

    def sort_by_name(d): return -d["count"], d["name"]

    sorted.sort(key=sort_by_name)
    return sorted


def make_top_songs(sp, songs, file, message, tag, total, db):
    """
    prints out the top songs for a given pd.series containing counts
    """
    if len(songs) > 10: songs = songs[0:10]

    file.write(message + "\n")

    for song in songs:
        id = song["ID"]
        track_info = get_song_info(sp, db, id)
        # track_info = sp.track(id)
        name = song["name"]
        count = song["count"]

        artist_names = format_artist_names(track_info["ArtistNames"])
    
        file.write(f"{count:3d}  {name}, by {artist_names}\n")
    
    file.write(f"Total songs played: {total}\n")

def make_formatted_top_songs(sp, songs, file, message, total, db, t="y", size=10):
    """
    make a formatted LaTeX minipage containing album artwork, artist names, song titles, and counts
    """
    # # add comma if necessary (assumes 4 digit numbers max)
    total = str(total)
    if len(total) == 4:
        total = total[0] + "," + total[1:]
    elif len(total) == 5:
        total = total[:2] + "," + total[2:]

    ltf = False

    if len(songs) < size//2:
        ltf = True

    if len(songs) > size:
        songs = songs[0:size]   
    

    file.write("\\noindent\\LARGE{" + f"{message}" + "}\\hfill \\large{" + f"Total songs played: {total}" + "}\\\\[10pt]\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")

    def write(song):
        
        id = song["ID"]
        # get information to write
        # track_info = sp.track(id)
        track_info = get_song_info(sp, db, id)
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

    upp = size//2
    if len(songs) < upp: upp = len(songs)
    for i in range(upp):
        write(songs[i])

    file.write("\\end{minipage}\\hfill%\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    
    if not ltf:
        upp = size 
        if len(songs) < upp: upp = len(songs)
        for i in range(size//2,upp):
            write(songs[i])
    
    file.write("\\end{minipage}\n")
    file.write("\\vspace{15pt}\n\n")

def make_user_stamp(i, length, file, user_url, display_name, yyyy):
    if i == length -1: pass
    elif i % 2 == 0: return
    file.write("\\vfill\\raggedleft\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    file.write("\\raggedleft")
    file.write("\\begin{minipage}{.75\\textwidth}\n")
    file.write("\\raggedleft\\large \\href{"+ user_url + "}{\\textbf{" + display_name +  "}}\\\\[2pt]\n")
    file.write(f"\\normalsize Yearly Recap: {yyyy}")
    file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
    file.write("\\begin{minipage}{.15\\textwidth}\n")
    file.write("\\includegraphics[width = \\textwidth]{" + f"{home_path}" + "/analysis/circpp.png}\n")
    file.write("\\end{minipage}\\end{minipage}\n")
    file.write("\\newpage\n")

#%%
def main():

    sp = get_auth()

    yyyy = 2022
    if len(sys.argv) == 2:
            yyyy = sys.argv[1]

    # ========== USER INFORMATION
    me = sp.current_user()
    display_name = me["display_name"]

    # get profile photo
    urlretrieve(me["images"][0]["url"],f"{home_path}/analysis/pp.jpg")
    # make image a circle
    make_image_circular(f"{home_path}/analysis/pp.jpg",f"{home_path}/analysis/circpp.png")

    # get user url
    user_url = me["external_urls"]["spotify"]

    # ========== CREATE DATA FRAMES FOR EACH MONTH

    all_songs = pd.DataFrame(columns=["ID","Timestamp"])
    large_db = {}
    months = []

    for mm in range(1,13):

        path = f"{home_path}/data/{yyyy}-{mm:02d}"
        if os.path.exists(f"{path}-songlist.txt"):
            df = pd.read_csv(f"{path}-songlist.txt")
            all_songs = pd.concat([all_songs,df])
            months.append(mm)
        
        if os.path.exists(f"{path}-database.txt"):
            with open(f"{path}-database.txt","r") as f:
                db = json.loads(f.read())
                large_db.update(db)

    #%%

    pdf = open(f"{home_path}/analysis/part.tex", "w")

    # do yearly stats first
    year_cts = all_songs["ID"].value_counts()
    year_topsongs = sort_songs(sp, year_cts, large_db, num=60)
    year_total = year_cts.sum()

    make_formatted_top_songs(sp, year_topsongs, pdf, f"{yyyy}'s Top Songs", year_total, large_db, size = 22)
    make_user_stamp(1,1,pdf, user_url, display_name, yyyy)

    for i in range(len(months)):
        mm = months[i]
        tag = datetime.strftime(datetime.today().replace(month =mm, day=1), "%B")
        path = f"{home_path}/data/{yyyy}-{mm:02d}"
        df = pd.read_csv(f"{path}-songlist.txt")
        pic_str = f"m{i}-"

        m_cts = df["ID"].value_counts()
        m_topsongs = sort_songs(sp, m_cts, large_db)
        m_total = m_cts.sum()

        make_formatted_top_songs(sp, m_topsongs, pdf, f"{tag}'s Top Songs", m_total, large_db, t=pic_str)
        make_user_stamp(i,len(months),pdf, user_url, display_name, yyyy)


    pdf.close()

    os.system(f"{pdflatex_path} -output-directory={home_path}/analysis {home_path}/analysis/analysis.tex > {home_path}/analysis/pdflatex_output.txt")
    # delte auxillary files
    os.system(f"rm {home_path}/analysis/analysis.aux")
    os.system(f"rm {home_path}/analysis/analysis.log")
    os.system(f"rm {home_path}/analysis/analysis.out")
    os.system(f"rm {home_path}/analysis/*.jpg")
    os.system(f"rm {home_path}/analysis/*.png")
    os.system(f"rm {home_path}/analysis/part.tex")
    os.system(f"rm {home_path}/analysis/pdflatex_output.txt")

if __name__ == "__main__":
    main()
