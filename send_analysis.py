import os
from secrets import sender, sendee, password, python_path, home_path, gd_path

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime
import pytz; est = pytz.timezone("America/New_York")

today = datetime.today().astimezone(est)
s = datetime.strftime(today, "%m%d%y")
sf = datetime.strftime(today, "%B %d, %Y")
my = datetime.strftime(today,"%m-%Y")

port = 465  # For SSL

# Create a secure SSL context
context = ssl.create_default_context()

path = home_path

os.system(f"{python_path} {path}/analysis.py > {path}/analyses/{s}-analysis.txt")
os.system(f"cp {path}/data/{my}-recentlyplayed.txt {gd_path}/{my}-recentlyplayed.txt")
os.system(f"cp {path}/analyses/{s}-analysis.txt {gd_path}/analyses/{s}-analysis.txt")
with open(f"{path}/analyses/{s}-analysis.txt") as f:
    message = """"""

    s = f.readline()
    while (s != ""):
        message += s
        s = f.readline()

m = MIMEMultipart("alternative")
m["Subject"] = f"Today's Stats! {sf}"
m["From"] = sender
m["To"] = sendee

message = MIMEText(message, "plain")
m.attach(message)

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(sender, password)
    server.sendmail(sender, sendee, m.as_string())


