# Read email script
import imapclient
import pyzmail
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
email_addr = email
password = password

# kill function
def kill_script():
    from crontab import CronTab
    my_cron = CronTab(user = 'pi') # open cron editor
    for job in my_cron:
        if 'trade script ' in job.comment:
            job.month.every(12) # run trade script only in december
            my_cron.write()    

# email function
def email_plot():
    msg = MIMEMultipart()
    msg['Subject'] = 'Price Chart'
    msg['From'] = email_addr
    msg['To'] = email_addr
    file = 'plot.png'

    msg.attach(MIMEText("Ethereum prie chart."))
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(open(file, 'rb').read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
    msg.attach(attachment)

    print('Sending...')
    s = server = smtplib.SMTP('smtp.gmail.com:587') #smtp.gmail.com:587
    s.starttls()
    s.login(email_addr, password)
    s.sendmail(email_addr, email_addr, msg.as_string())
    s.quit()
    print('done')

# set up imap
imap_obj = imapclient.IMAPClient('imap.gmail.com', ssl = True)
imap_obj.login(email_addr, password)
imap_obj.select_folder('Requests', readonly = False) # look in Requests folder
UIDS = imap_obj.search('(UNSEEN)') # only read in un-read emails

if len(UIDS) > 0:
    raw_message = imap_obj.fetch([UIDS[0]], ['BODY[]', 'FLAGS'])
    message = pyzmail.PyzMessage.factory(raw_message[UIDS[0]]['BODY[]'])
    msg_subj = message.get_subject()
    msg_text = message.text_part.get_payload().decode(message.text_part.charset).upper()
    imap_obj.logout()
    if 'KILL' in msg_text:
        kill_script()
        print('kill script')
    elif 'PLOT' in msg_text:
        email_plot()
        print('email plot')
else:
    print('No new emails')
    


