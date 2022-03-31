# Spotify Stats

"Spotify Stats" was developed to allow Spotify users to collect and analyze their listening history. This implementation creates a database of the songs that the user listens to and at what time, then sends a daily recap to the user via email. An example recap is given in `./example_summary.html`.

*Note*: this project has recently been updated to provide `html` and `css` enriched emails containing recaps. Before, those were provided via LaTeX compiled `pdf`s (an example of an old pdf is provided in `pdf-example.pdf`). The move towards `html` hopes to make this code quicker, cleaner, and better for distribution on a cloud service, such as AWS. 

## Setup

*Note*: This software assumes that you are using a Linux distribution (I use wsl2 Ubuntu) with command line python (specifically Ananconda3). Otherwise, you may run into missing package errors with python and OS errors due to the use of bash commands from the `os` python package.

1. Sign up to be a spotify developer and create a personal app. From here, you can get the user specific information needed below. Make sure to set redirect URL to http://localhost:7777/callback . *This section unfinished*

2. Create the `./data/` directory. This is where the song databases will live (`./data/yyyy-mm-songlist.txt`). Also, this is where the local song information databases will live (`./data/yyyy-mm-database.txt`). See Outline for explanation.

3. Create the `./analysis` directory.

4. Create the `./secrets.py` file. This contains user specific information; it should contain these variables:
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
- `analysis.py`: using the database, creates an `html` file with the top ten songs from the day and month and places them in `./analysis/`. *New*: creates and extends a local song database each month, saving pertinent reused information, such as the song name, artists names and artist ID's, and the URL for the album artwork. This database is not essential (i.e. the file can be deleted and will be reproduced) but its existence will make the program much faster, as the analysis can check and see if the data is stored locally, and only access Spotify's servers to grab the information if necessary (after accessing, this data is then stored locally for future use).
- `send_analysis.py`: sends the .txt and .pdf files via email using the addresses within `secrets.py.` This file also backs up the current database to the `gd_path` directory, as well as the .txt file to the `analyses` directory within the `gd_path` directory. Running this file on its own will call `analysis.py`. The command line argument `y` will create the analysis for yesterday.
- `yearly_recap.py`: this creates a yearly recap of the user's top 20(ish) songs, as well as the top ten songs from each month of the given year. This is backed up to the user's `gd_path` and not sent to them via email. Automatically run when `send_analysis.py` is run.

<!-- PDF Features: produced LaTeX .pdf contains the user's top ten songs for the current day and current month. Each song's accompanying album artwork is a hyperlink to the song on Spotify, and number next to it represents the number of times that song was played in the current timeframe. A user specific timestamp is placed in the bottom right of the document, with a hyperlink to the user's profile. -->

## Automation

You can automate all of these tasks using cron. I have the `get_rp.py` file run once per hour, and the `send_analysis.py` file run once per day. Ensure that absolute paths are used, and any output is sent to file so that cron functions correctly.
