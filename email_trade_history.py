# email historical trade information weekly
# to be ran every 7 days
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# set working directory in raspberry
path = '/home/pi/Desktop/files'
os.chdir(path)

# read in private email information
f = open('account.txt') # read in account.txt
f_lines = f.readlines()
email = f_lines[0].split(': ',1)[1][0:len(f_lines[0].split(': ',1)[1])-1] # email address (send and recieve)
password = f_lines[1].split(': ',1)[1][0:len(f_lines[1].split(': ',1)[1])-1] # password
f.close()

sender = email
receiver = email
password = password


msg = MIMEMultipart()
msg['Subject'] = 'Historical Trade Information'
msg['From'] = sender
msg['To'] = receiver
file = 'trade_log.txt'

msg.attach(MIMEText("Aggregated data."))
attachment = MIMEBase('application', 'octet-stream')
attachment.set_payload(open(file, 'rb').read())
encoders.encode_base64(attachment)
attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
msg.attach(attachment)

print('Sending...')
s = server = smtplib.SMTP('smtp.gmail.com:587') #smtp.gmail.com:587
s.starttls()
s.login(sender, password)
s.sendmail(sender, receiver, msg.as_string())
s.quit()
print('done')
