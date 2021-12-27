# Spotify Stats

This project will create a database of songs played each month, and at the end of each day send a LaTeX generated `.pdf` containing the top songs from that day and so far that month.

- see an example `.pdf` in `./example_summary.pdf`

*Note*: private user variables should be placed in the file `./secrets.py`. These variables contain the spotify username, client ID, client secret, sender, sendee, and cc'd email address, as well as generalized paths, like the `pdflatex` path, home path, and `gd_path` (google drive path) for backups.

## Outline
- `get_rp.py` should be run each hour; this "gets recently played" songs.
- `analysis.py` compiles a text based summary and LaTeX generated `.pdf` of top songs for the day and month and places them in `./analysis`
- `send_analysis.py` sends the text and `/pdf` analyses to the email addresses within `secrets.py`