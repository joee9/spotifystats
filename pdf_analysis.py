#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
import os
import sys
from urllib.request import urlretrieve
import numpy as np
from PIL import Image, ImageDraw

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path, sender

path = home_path
python = python_path

os.system(f"{python} {path}/get_rp.py >> {path}/newsongs.txt")
os.system(f"rm {path}/newsongs.txt")

mode = "top_10"
tf = "dm"

yesterday = False
if len(sys.argv) == 2 and sys.argv[1] == "y":
    yesterday = True
# yesterday = True
# yesterday = False

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

def make_counts(df,date,end):
    songs = pd.DataFrame(columns=["URI","Timestamp"])
    for i in range(len(df)):
        timestamp = df.iloc[i,1]
        parsed = parser.parse(timestamp).astimezone(est)
        if  parsed > date and parsed < end:
            songs = songs.append(df.iloc[i,:])
    
    return songs["URI"].value_counts()

def make_formatted_top_songs(counts, file, tag, message):
    a_len_limit = 36
    len_limit = 30
    keys = counts.keys()
    total = counts.sum()
    ltf = False
    if len(keys) < 5:
        ltf = True

    if len(keys) > 10:
        keys = keys[0:10]   

    if tag == "today":
        t = "d"
    elif tag == "this month":
        t = "m"
    
    file.write("\\noindent\\LARGE{" + f"{message}" + "}\\hfill \\large{" + f"Total songs {tag}: {total}" + "}\\\\[10pt]\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")

    def write(id):
        track_info = sp.track(id)
        urlretrieve(track_info["album"]["images"][0]["url"], f"{path}/analyses/pdf/{t}{i}.jpg")
        name = track_info["name"]
        count = f"({counts[id]})"
        if len(name) > len_limit:
            name = name[0:len_limit-3] + "..."
        count = f"({counts[id]}) "
        artist_names = count + format_artist_names(track_info)
        if len(artist_names) > a_len_limit:
            artist_names = artist_names[0:a_len_limit-3] + "..."

        file.write("\\begin{minipage}{.2\\textwidth}\n")
        file.write("\\includegraphics[width = \\textwidth]{" + f"{home_path}/analyses/pdf/{t}{i}" + ".jpg}\n")
        file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
        file.write("\\begin{minipage}{.75\\textwidth}\n")
        file.write("\\small \\textbf{" + f"{name}" + "}\\\\[2pt]\n")
        file.write("\\footnotesize" + f" {artist_names}\n")
        file.write("\end{minipage}\\\\[5pt]\n")
        file.write("\n")

    upp = 5
    if len(keys) < upp: upp = len(keys)
    for i in range(upp):
        write(keys[i])

    file.write("\\end{minipage}\\hfill%\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    
    if not ltf:
        upp = 10 
        if len(keys) < upp: upp = len(keys)
        for i in range(5,upp):
            write(keys[i])
    
    file.write("\\end{minipage}\n")
    file.write("\\vspace{15pt}\n\n")




my = datetime.strftime(datetime.today().astimezone(est), "%m-%Y")
df = pd.read_csv(f"{path}/data/{my}-recentlyplayed.txt")

#%%
dates = []
messages = []
tags = []

day_cutoff = datetime.today().astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)
month_cutoff = datetime.today().astimezone(est).replace(day=1, second=0, minute=0, hour=0, microsecond=0)
end = datetime.today().astimezone(est)


if yesterday:
    
    day_cutoff = day_cutoff - timedelta(days=1)

    m = int(datetime.strftime(day_cutoff,"%m"))
    month_cutoff = datetime.today().astimezone(est).replace(month=m, day=1, second=0, minute=0, hour=0, microsecond=0)
    
    end = datetime.today().astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)

today_str = datetime.strftime(day_cutoff,"%B %d, %Y")

# print(day_cutoff, month_cutoff, end)

#%%

if tf == "today":
    messages.append("Today's Top Songs")
    dates.append(day_cutoff)
    tags.append("today")

elif tf == "month":
    messages.append("This Month's Top Songs")
    dates.append(month_cutoff)
    tags.append("this month")

elif tf == "dm":
    messages.append("Today's Top Songs")
    dates.append(day_cutoff)
    tags.append("today")
    messages.append("This Month's Top Songs")
    dates.append(month_cutoff)
    tags.append("this month")
    
# with open(f"{path}/analyses/pdf/header.tex", "w") as f:
#     f.write()


output = open(f"{path}/analyses/pdf/part.tex", "w")


for i in range(len(dates)):
    date = dates[i]
    tag = tags[i]
    counts = make_counts(df, date, end)
    # top_songs(counts, mode)
    make_formatted_top_songs(counts,output,tag,messages[i])

me = sp.current_user()
urlretrieve(me["images"][0]["url"],f"{home_path}/analyses/pdf/pp.jpg")
display_name = me["display_name"]

img = Image.open(f"{home_path}/analyses/pdf/pp.jpg")

height,width = img.size
lum_img = Image.new('L', [height,width] , 0)

draw = ImageDraw.Draw(lum_img)
draw.pieslice([(0,0), (height,width)], 0, 360, 
            fill = 255, outline = "white")
img_arr = np.array(img)
lum_img_arr = np.array(lum_img)
final_img_arr = np.dstack((img_arr,lum_img_arr))

img = Image.fromarray(final_img_arr)
img.save(f"{home_path}/analyses/pdf/circpp.png")

output.write("\\vfill\\raggedleft\n")
output.write("\\begin{minipage}{.47\\textwidth}\n")
output.write("\\raggedleft")
output.write("\\begin{minipage}{.75\\textwidth}\n")
output.write("\\raggedleft\\large \\textbf{" + f"{display_name}" +  "}\\\\[2pt]\n")
# output.write("\\raggedleft\\large " + f"{display_name}" +  "\\\\[2pt]\n")
output.write(f"\\normalsize {today_str}")
output.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
output.write("\\begin{minipage}{.2\\textwidth}\n")
output.write("\\includegraphics[width = \\textwidth]{" + f"{home_path}" + "/analyses/pdf/circpp.png}\n")
output.write("\\end{minipage}\\end{minipage}\n")


output.close()

#%%
# time.sleep(1)
os.system(f"{pdflatex_path} -output-directory={path}/analyses/pdf {path}/analyses/pdf/analysis.tex > {path}/analyses/pdf/pdflatex_output.txt")
os.system(f"rm {path}/analyses/pdf/analysis.aux")
os.system(f"rm {path}/analyses/pdf/analysis.log")
os.system(f"rm {path}/analyses/pdf/*.jpg")
os.system(f"rm {path}/analyses/pdf/*.png")
os.system(f"rm {path}/analyses/pdf/part.tex")
os.system(f"rm {path}/analyses/pdf/pdflatex_output.txt")

# time = parser.isoparse(time_stamp)
# time_est = time.astimezone(est)
# time_print = datetime.strftime(time_est, "%c")