# Kraken Account - run on the 1st and 16th of every month and whenever deposit/withdraw placed
# Run in python2
import csv
import random
import string
import ccxt
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import string
import time
import os

# Set working directory in raspberry
path = '/home/pi/Desktop/files'
os.chdir(path)

# Read in account information
f = open('account.txt') # read in account.txt
f_lines = f.readlines()
email = f_lines[0].split(': ',1)[1][0:len(f_lines[0].split(': ',1)[1])-1] # email address (send and recieve)
password = f_lines[1].split(': ',1)[1][0:len(f_lines[1].split(': ',1)[1])-1] # email password
api_key = f_lines[2].split(': ',1)[1][0:len(f_lines[2].split(': ',1)[1])-1] # kraken api key
api_secret = f_lines[3].split(': ',1)[1] # kraken api secret
f.close()

# connect to kraken
kraken = ccxt.kraken()
kraken.apiKey = api_key
kraken.secret = api_secret
balance = kraken.fetchBalance()
usd = round(balance['USD']['total'],2)


# ID generator -- won't create duplicates
def create_id(I):
    id_num = I[0][1]
    while id_num in str(I): 
        letters = string.ascii_letters[26:]
        a = letters[random.randint(0,25)]
        b = letters[random.randint(0,25)]
        c = str(random.randint(1,9))
        id_num = a+b+c
    return(id_num)

# update account balance to current balance
def kraken_balance():
    for i in range(0, len(I)):
        I[i][2] = round(float(I[i][3]) * usd, 2)

# input new clients or deposit or withdraw old clients
def edit_I():
    kraken_balance()
    if '-01 ' in now_date or '-16 ' in now_date:
        print('Bi-monthly Update')
        action_log = ['',now_date, 'Bi-monthly Balance Update', '']
    else:
        # edit clients shares
        I_new = input('[C]reate new investor profile or [E]dit an existing profile? (c/e): ')
        if I_new.upper() == 'C':
            new_name = input("New investor's name: ")
            new_id = create_id(I)
            amount = input('Amount Invested ($): ')
            email = input('Email Address: ')
            dummy_percent = 0.0
            new_investor = [new_name, new_id, amount, dummy_percent, email]
            I.append(new_investor)
            action_log = ['',now_date, new_id + ' deposit ' + str(amount), '']
            print('new investor added')
        if I_new.upper() == 'E':
            user_id = input('User ID: ')
            action = input('Withdraw or Deposit (w/d): ')
            amount = input('Amount ($): ')
            for i in range(0, len(I)): # find which I to change
                if user_id in I[i]:
                    user = i
            if action.upper() == 'D':
                I[user][2] = float(I[user][2]) + float(amount)
                action_log = ['',now_date, user_id + ' deposit ' + str(amount), '']
            elif action.upper() == 'W':
                I[user][2] = float(I[user][2]) - float(amount)
                action_log = ['',now_date, user_id + ' withdraw ' + str(amount), '']
            print('edit old investor')
    # get balance and percent share
    new_balance = new_balance_func()
    new_percent_share(new_balance)
    csv_write(new_balance, action_log)


# Calculate new account balance
def new_balance_func():
    new_balance = 0
    for i in range(0, len(I)):
        new_balance += float(I[i][2])
    return(float(new_balance))

# Calculate percent share
def new_percent_share(new_balance):
    for i in range(0, len(I)):
        I[i][3] = float(I[i][2])/new_balance
    return(I)

# write out to csv
def csv_write(new_balance, action_log):
    with open('k_account.csv', 'wb') as csv_file:
        file_writer = csv.writer(csv_file)
        balance = [' ', 'Account Balance ($)', new_balance]
        date_header = [' ','Last Updated:', now_date]
        header = ['Secret Name', 'ID #', 'Invested ($)', '% of Pot', 'Email']
        history.append(action_log)
        file_writer.writerow(balance)
        file_writer.writerow(date_header)
        file_writer.writerow(' ') # empty row
        file_writer.writerow(header)
        for i in range(0, len(I)):
            file_writer.writerow(I[i])
        file_writer.writerow(' ') # empty row
        file_writer.writerow(' ') # empty row
        for i in range(0, len(history)):
            file_writer.writerow(history[i])

# Update Google Sheets function
def update_sheet():
    # wait 3 seconds to write out k_account.csv
    time.sleep(3)
    # Connect to Google Sheets
    print('Connecting to Google Sheets...')
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    gc = gspread.authorize(credentials)
    wks = gc.open("Account").sheet1

    # read in k_account.csv
    f = open('k_account.csv')
    f_reader = csv.reader(f)
    f_data = list(f_reader)
    f.close()

    # Edit Google Sheet 'Account'
    for i in range(0, len(f_data)):
        cell_range = 'A' + str(i+1) + ':B' + str(i+1)
        row_text = f_data[i][1:3]

        # upload to sheets
        if len(row_text) > 0:
            cell_list = wks.range(cell_range)
            for j in range(0,len(row_text)):
                cell_list[j].value = row_text[j]
            wks.update_cells(cell_list)
        else:
            cell_list = wks.range(cell_range)
            row_text = [' ',' ']
            for j in range(0,len(row_text)):
                cell_list[j].value = row_text[j]
            wks.update_cells(cell_list)           
    print('Done.')
    

# read in k_account
f = open('k_account.csv')
f_reader = csv.reader(f)
f_data = list(f_reader)
for i in range(0, len(f_data)): # find client info
    if '' not in f_data[i]: # if len(f_data[i]) > 0:
        index = i 
    if 'History' in f_data[i]:
        index_2 = i
if 'Date' in f_data[len(f_data)-1]:
    I = f_data[4:(index+1)]
else:
    I = f_data[4:(index-1)]
old_balance = str(f_data[0][2])
history = f_data[index_2:]
f.close()

# get date/time
now = str(datetime.datetime.now())
now_date = now[0:16]

print(I)

# Run
edit_I() # edit csv 
update_sheet() # update google sheets

    


    


