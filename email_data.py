# email historical data weekly

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os


sender = 'aocapital1@gmail.com'
receiver = 'aocapital1@gmail.com'
password = 'A.O.capital!'


msg = MIMEMultipart()
msg['Subject'] = 'Data'
msg['From'] = sender
msg['To'] = receiver
file = 'xbt_data.csv'

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
