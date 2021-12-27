# Spotify Stats

"Spotify Stats" was developed to allow Spotify users to collect and analyze their listening history. This implementation creates a database of the songs that the user listens to and at what time, then sends a daily recap to the user via email. An example recap is given in `./example_summary.pdf`.

## Setup

*Note*: This software assumes that you are using a Linux distribution (I use wsl2 Ubuntu) with command line python (specifically Ananconda3) and LaTeX (I use texlive-full) installed. Otherwise, you may run into missing package errors with LaTeX and python and OS errors due to the use of bash commands from the `os` python package.

1. Sign up to be a spotify developer and create a personal app. From here, you can get the user specific information needed below. Make sure to set redirect URL to http://localhost:7777/callback . *This section unfinished*

2. Create the `./data/` directory. This is where the song databases will live (`./data/mm-yyyy-songlist.txt`).

3. Modify the path within `./analysis/analysis.tex` such that it points to your specific `./analysis/` directory. This points to my personal directory.

4. create the `./secrets.py` file. This contains user specific information; it should contain these variables:
    - Spotify specific:
        - `username` (str): the user's login username, usually an email address
        - `client_id` (str): the user's client ID; get from step 1.
        - `client_secret` (str): the user's secret key; get from step 1.
    - email specific:
        - `sender` (str): the email address from which emails will be sent. I created a special, separate gmail account for this purpose. *Note*: you may need to turn off some security settings for the google account in order for it to allow this code to send emails
        - `password` (str): the password for the above email account
        - `sendee` (str) and `cc` (str): the address(es) for emails to be sent to. For multiple emails, separate by commas and spaces (", ")
    - path specific:
        - `home_path` (str): the absolute path to the `spotifystats` directory
        - `pdflatex_path` (str): the absolute path to the pdflatex compiler
        - `python_path` (str): the absolute path to the python distribution
        - `gd_path` (str): the absolute path to the backup folder; in my case, a google drive (gd) folder on the C: drive. Make sure that within the `gd_path`, there is an `analyses` directory.

## Outline

There are three important files:
- `get_rp.py`: "gets recently played" songs. The file adds the user's recently played songs to the current month's database.
- `analysis.py`: using the database, creates a LaTeX generated .pdf and a .txt file with the top ten songs from the day and month and places them in `./analysis/analysis.*`.
- `send_analysis.py`: sends the .txt and .pdf files via email using the addresses within `secrets.py.` This file also backs up the current database to the `gd_path` directory, as well as the .txt file to the `analyses` directory within the `gd_path` directory. Running this file on its own will call `analysis.py`. The command line argument `y` will create the analysis for yesterday.

## Automation

You can automate all of these tasks using cron. I have the `get_rp.py` file run once per hour, and the `send_analysis.py` file run once per day. Ensure that absolute paths are used, and any output is sent to file so that cron functions correctly.