# csv reader
import csv
import ccxt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os

# parameters: as %
take_profit = .05
stop_loss = .05

# set working directory in raspberry
# path = '/home/pi/Desktop/files'
# os.chdir(path)

# read in private information
f = open('account.txt') # read in account.txt
f_lines = f.readlines()
email = f_lines[0].split(': ',1)[1][0:len(f_lines[0].split(': ',1)[1])-1] # email address (send and recieve)
password = f_lines[1].split(': ',1)[1][0:len(f_lines[1].split(': ',1)[1])-1] # aocapital1@gmail.com password
api_key = f_lines[2].split(': ',1)[1][0:len(f_lines[2].split(': ',1)[1])-1] # kraken api key
api_secret = f_lines[3].split(': ',1)[1] # kraken api secret
f.close()

# email
def email(trade): # function with input 'buy/sell/close'
    sender = email
    receiver = email
    password = password

    msg = MIMEMultipart()
    msg['Subject'] = 'Trade'
    msg['From'] = sender
    msg['To'] = receiver

    now = str(datetime.datetime.now())
    now_date = now[0:16]
    
    message = 'Time stamp: ' + now_date + '\n\n' + 'Action: ' + trade + '\n\n' + 'price: ' + str(current_price)
    msg.attach(MIMEText(message))
    s = server = smtplib.SMTP('smtp.gmail.com:587') #smtp.gmail.com:587
    s.starttls()
    s.login(sender, password)
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()

# read in trade_hist
f = open('trade_hist.csv')
f_reader = csv.reader(f)
f_data = list(f_reader)

trade_sig = f_data[len(f_data)-1][2] # most recent trade
trade_price = float(f_data[len(f_data)-1][3]) # most recent price
trade_date = f_data[len(f_data)-1][1]
prev_sig = f_data[len(f_data)-2][2] # previous trade
f.close()

# Run script if there are not two consecutive trades (need opposing trades or a 'close' between two equal signals)
if(trade_sig != prev_sig):
    # read in current price
    f = open('current_price.txt')
    f_lines = f.readlines()
    current_date = f_lines[0] # read in date + time intervals
    current_price = float(f_lines[1]) # price
    f.close()

    # read in previous volume
    f = open('volume.txt')
    f_lines = f.readlines()
    vol_close = float(f_lines[0]) # volume for closing trade
    f.close()

    # kraken
    kraken = ccxt.kraken({
        'apiKey': api_key,
        'secret': api_secret})

    # account balance to determine volume
    balance = (kraken.fetch_balance())
    usd = (balance['free'][u'USD'])/2
    vol_open = round((usd/current_price)*.9,4) # volume for new trade after close signal, 90% of available balance rounded to 4 digits
    vol_open = .002

    # volume for opening positions
    if (prev_sig == 'close' and trade_sig != 'close'):
        vol = vol_open # if trade after closed position
        # write out new volume
        f = open('volume.txt', 'w')
        f.write(str(vol))
        f.close()
    else:
        vol = vol_close*2 # if trade after previous buy/sell do not re-write new volume
        
        
    # write close signal function, signal = close_short or close_long
    def write_close(signal):
        f = open('trade_hist.csv', 'ab')
        f_writer = csv.writer(f)
        f_writer.writerow(['4', trade_date, signal, str(current_price)])
        f.close()


    # trade Execution
    # Buy
    if(trade_date == current_date and trade_sig == 'buy'):
        print('buy')
        # use vol
        # order = kraken.create_market_buy_order ('BTC/USD', vol, {'leverage': 2}) # kraken long position at leverage 2:1
        email('Buy')
    # Sell 
    elif(trade_date == current_date and trade_sig == 'sell'):
        print('sell')
        # use vol
        # order = kraken.create_market_sell_order ('BTC/USD', vol, {'leverage': 2}) # kraken short position at leverage 2:1
        email('Sell')
    # Close long 
    elif(current_price > trade_price*(1+take_profit) and trade_sig == 'buy'
         or current_price < trade_price*(1-stop_loss) and trade_sig == 'buy'):
        print('take profit or stop loss')
        vol = vol_close
        # order = kraken.create_market_sell_order ('BTC/USD', vol, {'leverage': 2}) # close long with equal volume sell
        write_close('close') # write close to trade_hist.csv
        email('Close long')
    # Close short
    elif(current_price > trade_price*(1+stop_loss) and trade_sig == 'sell'
         or current_price < trade_price*(1-take_profit) and trade_sig == 'sell'):
        print('stop loss or take profit')
        vol = vol_close
        # order = kraken.create_market_buy_order ('BTC/USD', vol, {'leverage': 2}) # close sell with equal volume buy
        write_close('close') # write close to trade_hist.csv
        email('Close short')
    # Do nothing
    else:
        print('hold')



# view results
print(trade_sig)
print(trade_price)
print(trade_date)
print(current_price)
print(current_date)
print(usd)
print('volume: ' + str(vol))
print(os.getcwd())

