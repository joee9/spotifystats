#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
from dateutil.tz import tzutc
import os
import sys
import time
from urllib.request import urlretrieve

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path

path = home_path
python = python_path

# os.system(f"{python} {path}/get_rp.py >> {path}/newsongs.txt")
# os.system(f"rm {path}/newsongs.txt")

# if len(sys.argv) == 0 or len(sys.argv) == 1:
#     mode = "top_10"
mode = "top_10"
tf = "dm"
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

#%%

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
    if mode == "top_10" and len(keys) > 10:
        keys = keys[0:10]

    for id in keys:
        track_info = sp.track(id)
        name = track_info["name"]
        count = counts[id]
        artist_names = format_artist_names(track_info)
    
        print(f"{count:3d}  {name}, by {artist_names}")

def make_counts(df,date):
    songs = pd.DataFrame(columns=["URI","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > date:
            songs = songs.append(df.iloc[i,:])
    
    return songs["URI"].value_counts()

def make_formatted_top_songs(counts, file, tag, message):
    keys = counts.keys()
    if len(keys) > 5:
        keys = keys[0:5]
    
    if tag == "today":
        t = "d"
    elif tag == "this month":
        t = "m"
    
    file.write("\\begin{center}")
    file.write("\\LARGE{" + f"{message}" + "}")
    file.write("\\end{center}")

    for i in range(len(keys)):
        id = keys[i]
        track_info = sp.track(id)
        urlretrieve(track_info["album"]["images"][0]["url"], f"{path}/analyses/pdf/{t}{i}.jpg")
        name = track_info["name"]
        count = counts[id]
        artist_names = format_artist_names(track_info)

        file.write("\\noindent\\begin{minipage}{.075\\textwidth}\n")
        file.write("\\LARGE{" + f"{i+1}" + "}\n")
        file.write("\\end{minipage}%\n")
        file.write("\\begin{minipage}{.1\\textwidth}\n")
        file.write("\\includegraphics[width = \\textwidth]{" + f"{home_path}/analyses/pdf/{t}{i}" + ".jpg}\n")
        file.write("\\end{minipage}%\n")
        file.write("\\begin{minipage}{.05\\textwidth}\n")
        file.write("\\end{minipage}%\n")
        file.write("\\begin{minipage}{.375\\textwidth}\n")
        file.write("\\large \\centering\n")
        file.write(f"{name}\n")
        file.write("\\end{minipage}%\n")
        file.write("\\begin{minipage}{10pt}\n")
        file.write("%\n")
        file.write("\\end{minipage}%\n")
        file.write("\\begin{minipage}{.325\\textwidth}\n")
        file.write("\\large\\centering\n")
        file.write(f"{artist_names}\n")
        file.write("\\end{minipage}%\n")
        file.write("\\hfill%\n")
        file.write("\\begin{minipage}{.075\\textwidth}\n")
        file.write("\\centering\\Large{(" + f"{count}" + ")}\n")
        file.write("\\end{minipage}\n")
        if i != len(keys) - 1:
            file.write("\\vspace{5pt}\n\n")
    

    total = counts.sum()
    file.write("\\begin{center}\n")
    file.write("\\Large\centering\n")
    file.write(f"Total songs {tag}: {total}\n")
    file.write("\\end{center}\n")


my = datetime.strftime(datetime.today().astimezone(est), "%m-%Y")
df = pd.read_csv(f"{path}/data/{my}-recentlyplayed.txt")

#%%
dates = []
messages = []
tags = []

day_cutoff = datetime.today().astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)
month_cutoff = datetime.today().astimezone(est).replace(day=1, second=0, minute=0, hour=0, microsecond=0)

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
    
# with open(f"{path}/analyses/pdf/header.tex", "w"):


output = open(f"{path}/analyses/pdf/part.tex", "w")


for i in range(len(dates)):
    date = dates[i]
    tag = tags[i]
    counts = make_counts(df, date)
    # top_songs(counts, mode)
    make_formatted_top_songs(counts,output,tag,messages[i])

output.close()
time.sleep(1)
os.system(f"{pdflatex_path} -output-directory={path}/analyses/pdf {path}/analyses/pdf/analysis.tex > {path}/analyses/pdf/pdflatex_output.txt")
os.system(f"rm {path}/analyses/pdf/analysis.aux")
os.system(f"rm {path}/analyses/pdf/analysis.log")
os.system(f"rm {path}/analyses/pdf/*.jpg")
os.system(f"rm {path}/analyses/pdf/part.tex")
os.system(f"rm {path}/analyses/pdf/pdflatex_output.txt")

# time = parser.isoparse(time_stamp)
# time_est = time.astimezone(est)
# time_print = datetime.strftime(time_est, "%c")