# crypto trade script using krakenex
# Load libraries
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import datetime
import os
import krakenex
import time

# Set working directory in raspberry
path = '/home/pi/Desktop/files'
os.chdir(path)

# Stop loss
stop_loss = .02
take_profit = .08

# Read in account information
f = open('account.txt') # read in account.txt
f_lines = f.readlines()
email = f_lines[0].split(': ',1)[1][0:len(f_lines[0].split(': ',1)[1])-1] # email address (send and recieve)
password = f_lines[1].split(': ',1)[1][0:len(f_lines[1].split(': ',1)[1])-1] # email password
api_key = f_lines[2].split(': ',1)[1][0:len(f_lines[2].split(': ',1)[1])-1] # kraken api key
api_secret = f_lines[3].split(': ',1)[1] # kraken api secret
f.close()

# Email Function
def send_email(trade): # function with input 'buy/sell/close'
    sender = email
    receiver = email

    msg = MIMEMultipart()
    msg['Subject'] = 'Trade'
    msg['From'] = sender
    msg['To'] = receiver
    file = 'plot.png'

    now = str(datetime.datetime.now())
    now_date = now[0:16]
    
    message = 'Time stamp: ' + now_date + '\n\n' + 'Action: ' + trade + '\n\n' + 'price: ' + str(current_price)
    msg.attach(MIMEText(message))
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(open(file, 'rb').read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
    msg.attach(attachment)
    s = server = smtplib.SMTP('smtp.gmail.com:587') #smtp.gmail.com:587
    s.starttls()
    s.login(sender, password)
    s.sendmail(sender, receiver, msg.as_string())
    s.quit()

# Order function
def order_func(action, pair, volume, volume2, stop_price, take_price):
    print('trading...')
    if(action == 'buy'):
        action2 = 'sell'
    elif(action == 'sell'):
        action2 = 'buy'
    order = k.query_private('AddOrder',
                                 {'pair': pair,
                                  'type': action,
                                  'ordertype': 'market',
                                  'volume': volume,
                                  'leverage': '2:1'})
    time.sleep(2)
    order2 = k.query_private('AddOrder',
                                 {'pair': pair,
                                  'type': action2,
                                  'ordertype': 'take-profit',
                                  'volume': volume2,
                                  'price': take_price,
                                  'leverage': '2:1'})
    time.sleep(2)
    order3 = k.query_private('AddOrder',
                                 {'pair': pair,
                                  'type': action2,
                                  'ordertype': 'stop-loss',
                                  'volume': volume2,
                                  'price': stop_price,
                                  'leverage': '2:1'})                           
    print('trade complete.')
    # send email
    send_email(action)
    # write trade info to trade_log.txt
    f = open('trade_log.txt','a')
    f.write('\n\n' + str(datetime.datetime.now())[0:16])
    f.write('; Error: ' + str(order['error']))
    f.write('; Action: ' + str(order['result']['descr']['order']))
    f.write('; ID: ' + str(order['result']['txid'])[2:][:-2])
    f.write('\nTake_profit-->')
    f.write(' Error: ' + str(order2['error']))
    f.write('; Action: ' + str(order2['result']['descr']['order']))
    f.write('; ID: ' + str(order2['result']['txid'])[2:][:-2])
    f.write('\nstop_loss-->')
    f.write(' Error: ' + str(order3['error']))
    f.write('; Action: ' + str(order3['result']['descr']['order']))
    f.write('; ID: ' + str(order3['result']['txid'])[2:][:-2])  
    f.close()
    
# Close open trades
def close_open_func():
    open_order = k.query_private('OpenOrders') # get open orders
    while len(open_order['result']['open']) > 0: 
        open_order_id = list(open_order['result']['open'])[0] # id
        k.query_private('CancelOrder', {'txid': open_order_id}) # cancel order
        open_order = k.query_private('OpenOrders') # re_open order to get new length
    time.sleep(2) # sleep 2 second to allow to cancel orders


# read in trade_hist
f = open('trade_hist.csv')
f_reader = csv.reader(f)
f_data = list(f_reader)
trade_sig = f_data[len(f_data)-1][2] # most recent trade
trade_price = float(f_data[len(f_data)-1][3]) # most recent price
trade_date = f_data[len(f_data)-1][1]
prev_sig = f_data[len(f_data)-2][2] # previous trade
f.close()

# Read in current price
f = open('current_price.txt')
f_lines = f.readlines()
current_date = f_lines[0] # read in date + time intervals
current_date = current_date[0:(len(current_date)-1)] # remove '\n' from current_date
current_price = float(f_lines[1]) # price
f.close()

# Connect to Kraken
k = krakenex.API(key = api_key, secret = api_secret)

# Available volume for new trade
balance = k.query_private('Balance')
balance = balance['result'] # clean 'balance'
usd = float(balance['ZUSD'])
volume_open = round(((usd*.5)/current_price),4)

# Get prev_volume from open position
open_order = k.query_private('OpenOrders')
if(len(open_order['result']['open']) > 0):
    open_order_id = list(open_order['result']['open'])[0]
    prev_vol = open_order['result']['open'][open_order_id]['vol']



# Execute Trade
if(trade_sig != prev_sig):
    if(len(open_order['result']['open']) > 1):
        if(trade_date == current_date and trade_sig == 'buy'):
            close_open_func() # cancel open orders
            action = 'buy'
            pair = 'XETHZUSD'
            volume = str(float(prev_vol)*2) # use 2x volume to close previous trade and open new trade
            volume2 = prev_vol
            stop_price = str(round(current_price*(1-stop_loss),1))
            take_price = str(round(current_price*(1+take_profit),1))
            order_func(action, pair, volume, volume2, stop_price, take_price)
            print('buy reverse')
        elif(trade_date == current_date and trade_sig == 'sell'):
            close_open_func() # cancel open orders
            action = 'sell'
            pair = 'XETHZUSD'
            volume = str(float(prev_vol)*2) # use 2x volume to close previous trade and open new trade
            volume2 = prev_vol
            stop_price = str(round(current_price*(1+stop_loss),1))
            take_price = str(round(current_price*(1-take_profit),1))
            order_func(action, pair, volume,  volume2, stop_price, take_price)
            print('sell reverse')
    elif(len(open_order['result']['open']) < 2):
        if(trade_date == current_date and trade_sig == 'buy'):
            close_open_func() # cancel open orders
            action = 'buy'
            pair = 'XETHZUSD'
            volume = volume_open # use volume from account
            volume2 = volume
            stop_price = str(round(current_price*(1-stop_loss),1))
            take_price = str(round(current_price*(1+take_profit),1))
            order_func(action, pair, volume,  volume2, stop_price, take_price)
            print('buy new')
        elif(trade_date == current_date and trade_sig == 'sell'):
            close_open_func() # cancel open orders
            action = 'sell'
            pair = 'XETHZUSD'
            volume = volume_open # use volume from account
            volume2 = volume # close volumes
            stop_price = str(round(current_price*(1+stop_loss),1))
            take_price = str(round(current_price*(1-take_profit),1))
            order_func(action, pair, volume,  volume2, stop_price, take_price)
            print('sell new')
    else:
        print('Hold.')

print('Script complete.')
print('\nCurrent date: ')
print(current_date)
print('\ntrade date: ')
print(trade_date)
print('\ncurrent price: ')
print(current_price)

