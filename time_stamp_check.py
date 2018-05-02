# Time stamp check: Run daily at same time as 'timestamp_check.R'
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from decimal import Decimal
import time

# wait 60 seconds for R script to run
time.sleep(60)

# set working directory in raspberry
path = '/home/pi/Desktop/files'
os.chdir(path)

# Email function
def send_email():
    f = open('account.txt') # read in account.txt
    f_lines = f.readlines()
    email = f_lines[0].split(': ',1)[1][0:len(f_lines[0].split(': ',1)[1])-1] # email address (send and recieve)
    password = f_lines[1].split(': ',1)[1][0:len(f_lines[1].split(': ',1)[1])-1] # password
    f.close()

    sender = email
    receiver = email
    password = password

    msg = MIMEMultipart()
    msg['Subject'] = 'Time Stamp ALERT'
    msg['From'] = sender
    msg['To'] = receiver

    message = text + '\n' + 'Algorithm is lagging by ' + lag +' minutes.\n\n' + kraken_time + '\n' + algo_time

    msg.attach(MIMEText(message))

    print('sending')
    s = server = smtplib.SMTP('smtp.gmail.com:587') #smtp.gmail.com:587
    s.starttls()
    s.login(sender, password)
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()
    print('done')


if (os.path.exists('timestamp_ALERT.txt')):
    # read in file
    f = open('timestamp_ALERT.txt')
    f_lines = f.readlines()
    text = f_lines[0]
    kraken_time = f_lines[1]
    algo_time = f_lines[2]
    f.close()
    k = kraken_time[(kraken_time.find(': ')+2):-1]
    a = algo_time[(algo_time.find(': ')+2):]
    lag = str(float(Decimal(k) - Decimal(a))/60) # in minutes
    
    # send email
    send_email()
    
    # delete file
    os.remove('timestamp_ALERT.txt')
    print('alert processed')
else:
    print('no alert')




