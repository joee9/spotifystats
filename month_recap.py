#%%
import pandas as pd
import spotipy.util as util
import spotipy
from datetime import datetime
import pytz; est = pytz.timezone("America/New_York")
from dateutil import parser
from dateutil.tz import tzutc
import sys
import os
from urllib.request import urlretrieve
from pdf_analysis import make_formatted_top_songs

from secrets import username, client_id, client_secret, home_path, python_path, pdflatex_path

path = home_path
python = python_path

# if len(sys.argv) != 2:
#     print("Please insert a month in mm-yyyy format!")

month = "11-2021"

redirect_uri = 'http://localhost:7777/callback'
# scope = 'user-read-recently-played'
scope = "user-top-read"

token = util.prompt_for_user_token(username=username, scope=scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

sp = spotipy.Spotify(auth=token)


#%%
rp = pd.read_csv(f"{path}/data/{month}-recentlyplayed.txt")
song_counts = rp["URI"].value_counts()

songs = rp["URI"]

if os.path.exists(f"{path}/data/{month}-artists.txt"):
    artists_df = pd.read_csv(f"{path}/data/{month}-artists.txt")

    # if len(artists_df) == len(songs):
    #     make_df = False

else:
    artists_df = pd.DataFrame(columns=["URI"])

    print(f"Cycling through all {len(songs)} songs.")

    for i in range(len(songs)):
        song = songs[i]
        track_info = sp.track(song)
        artists = track_info["album"]["artists"]
        for artist in artists:
            artist_uri = artist["uri"]
            artists_df = artists_df.append({
                "URI": artist_uri,
            }, ignore_index=True)
        if i % 50 == 0: print(f"Song {i} reached.")
    
    artists_df.to_csv(f"{path}/data/{month}-artists.txt",index=False)
        
    
    

#%%
artist_counts = artists_df["URI"].value_counts()
artists = artist_counts.keys()

for i in range(10): 
    artist = sp.artist(artists[i])
    name = artist["name"]
    count = artist_counts[i]
    print(f"{i+1:2d}.  {name:30}, {count}")

sp.artist(artists[0])



#%%
# os.system(f"{pdflatex_path} -output-directory={path}/analyses/pdf {path}/analyses/pdf/analysis.tex > {path}/analyses/pdf/pdflatex_output.txt")
# os.system(f"rm {path}/analyses/pdf/analysis.aux")
# os.system(f"rm {path}/analyses/pdf/analysis.log")
# os.system(f"rm {path}/analyses/pdf/*.jpg")
# os.system(f"rm {path}/analyses/pdf/part.tex")
# os.system(f"rm {path}/analyses/pdf/pdflatex_output.txt")
