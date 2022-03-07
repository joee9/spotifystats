# Joe Nyhan, 31 December 2021; updated 7 January 2021
# Creates a LaTeX generated yearly summary; see yearly_sum_example.pdf

# TODO: update to write monthly databases

#%%

from auth import get_auth

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
from latex import make_fullpage_summary, make_formatted_top_songs, make_image_circular
from analysis import start_of_day_est
from count import get_counts


def make_user_stamp(i, length, file, stamp_info):
    display_name, user_url, pic_path, tag = stamp_info
    if i == length -1: pass
    elif i % 2 == 0: return
    file.write("\\vfill\\raggedleft\n")
    file.write("\\begin{minipage}{.47\\textwidth}\n")
    file.write("\\raggedleft")
    file.write("\\begin{minipage}{.75\\textwidth}\n")
    file.write("\\raggedleft\\large \\href{"+ user_url + "}{\\textbf{" + display_name +  "}}\\\\[2pt]\n")
    file.write(f"\\normalsize {tag}")
    file.write("\\end{minipage}\\hspace{.05\\textwidth}%\n")
    file.write("\\begin{minipage}{.2\\textwidth}\n")
    file.write("\\includegraphics[width = \\textwidth]{" + pic_path + "}\n")
    file.write("\\end{minipage}\\end{minipage}\n")
    file.write("\\newpage\n")

def main():

    sp = get_auth()

    yyyy = 2022
    if len(sys.argv) == 2:
            yyyy = sys.argv[1]

    # ========== USER INFORMATION
    me = sp.current_user()
    display_name = me["display_name"]

    pp_path = f'{home_path}/analysis/pp.png'
    urlretrieve(me["images"][0]["url"],pp_path)
    make_image_circular(pp_path,pp_path)

    # get user url
    user_url = me["external_urls"]["spotify"]

    usr_info = display_name, user_url, pp_path, f'Yearly Recap: {yyyy}'

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

    #%%

    pdf = open(f"{home_path}/analysis/part.tex", "w")

    # do yearly stats first
    year_cts = get_counts(sp, all_songs, all_dbs)

    make_fullpage_summary(pdf, year_cts, all_dbs, usr_info, str(yyyy), pct=True)

    # monthly top songs
    for i in range(len(months)):
        mm = months[i]
        tag = datetime.strftime(datetime.today().replace(month =mm, day=1), "%B")
        path = f"{home_path}/data/{yyyy}-{mm:02d}"
        df = pd.read_csv(f"{path}-songlist.txt")

        if os.path.exists(f'{path}-counts.txt'):
            with open(f'{path}-counts.txt') as f:
                m_song_cts, m_artist_cts, m_album_cts, m_total = json.loads(f.read())
        else:
            m_song_cts, m_artist_cts, m_album_cts, m_total = get_counts(sp, df, all_dbs)
        
        last_ts = df.tail(1).to_numpy()[0][1]
        last_time = parser.parse(last_ts)
        cutoff_time = start_of_day_est(datetime.today()) - timedelta(days = 1)

        # write if counts file doesnt exist and falls in the right timeframe
        if last_time < cutoff_time and not os.path.exists(f'{path}-counts.txt'):
            with open(f'{path}-counts.txt','w') as f:
                cts = m_song_cts, m_artist_cts, m_album_cts, m_total
                f.write(json.dumps(cts))


        make_formatted_top_songs(m_song_cts, pdf, tag, m_total, large_track_db)
        make_user_stamp(i,len(months),pdf, usr_info)

    pdf.close()

    os.system(f"{pdflatex_path} -output-directory={home_path}/analysis {home_path}/analysis/analysis.tex > {home_path}/analysis/pdflatex_output.txt")
    # delte auxillary files
    os.system(f"rm {home_path}/analysis/analysis.aux")
    os.system(f"rm {home_path}/analysis/analysis.log")
    os.system(f"rm {home_path}/analysis/analysis.out")
    # os.system(f"rm {home_path}/analysis/*.jpg")
    os.system(f"rm {home_path}/analysis/*.png")
    os.system(f"rm {home_path}/analysis/part.tex")
    os.system(f"rm {home_path}/analysis/pdflatex_output.txt")

if __name__ == "__main__":
    main()
