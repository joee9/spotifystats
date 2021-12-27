#%%
import os
import sys
from secrets import sender, sendee, cc, password, python_path, home_path, gd_path

import smtplib, ssl
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from datetime import datetime, timedelta
import pytz; est = pytz.timezone("America/New_York")

yesterday = False
today = datetime.today().astimezone(est)
args = ""

if len(sys.argv) == 2 and sys.argv[1] == "y":
    d = datetime.today() - timedelta(days=1)
    today = d.astimezone(est).replace(second=0, minute=0, hour=0, microsecond=0)
    yesterday = True
    args = " y"

s = datetime.strftime(today, "%Y-%m%d")
sf = datetime.strftime(today, "%B %d, %Y")
my = datetime.strftime(today,"%m-%Y")

port = 465  # For SSL

# Create a secure SSL context
context = ssl.create_default_context()

path = home_path

os.system(f"{python_path} {path}/get_rp.py > {path}/output.txt")
os.system(f"{python_path} {path}/analysis.py{args} >> {path}/output.txt")
os.system(f"rm {path}/output.txt")
os.system(f"cp {path}/data/{my}-songlist.txt {gd_path}/{my}-songlist.txt")
os.system(f"cp {path}/analysis/analysis.txt {gd_path}/analyses/{s}-analysis.txt")

#%%

with open(f"{path}/analysis/analysis.txt") as f:
    message = """"""

    string = f.readline()
    while (string != ""):
        message += string
        string = f.readline()

m = MIMEMultipart()
m["Subject"] = f"Today's Stats! {sf}"
m["From"] = sender
m["To"] = sendee
m["CC"] = cc

message = MIMEText(message, "plain")
m.attach(message)

# s = datetime.strftime(today, "%m%d%y")
attachment = f"{path}/analysis/analysis.pdf"
with open(attachment, "rb") as a:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(a.read())
    

encoders.encode_base64(part)

part.add_header(
    "Content-Disposition",
    f"attachment; filename={s}-joesspotifystats.pdf",
)
m.attach(part)

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(sender, password)
    server.sendmail(sender, sendee.split(", ") + cc.split(", "), m.as_string())


