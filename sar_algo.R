# SAR Algorithm
# Run on 0 and 30 minutes

# load packages
suppressWarnings(library(quantmod))
suppressWarnings(library(TTR))

# set up directory on rasbperry
dir = '/home/pi/Desktop/files'
setwd(dir)

# Sar Paramaters
v = 0.031

# Get previous and current time intervals
prev_date = read.delim('current_price.txt', header = FALSE)[1,1]
new_date = prev_date + 1800

# wait 5 seconds to run to get new interval
Sys.sleep(5)

# create dummy ohlc.out to compare lengths
ohlc.out = 1
while(length(ohlc.out) == 1){ # run until the data downloads
  Sys.sleep(1) # wait 1 second before re try download
  pair = "XETHZUSD" 
  interval = '30'
  base.url = "https://api.kraken.com/0/public/OHLC"
  url <- paste0(base.url, "?", "pair=", pair, "&interval=", interval)
  
  
  # interval = minute
  ohlc.out <- jsonlite::fromJSON(url) 
}

# create data table
df = ohlc.out[[2]]$XETHZUSD
df = as.numeric(df) # change to numeric
df = matrix(data = df, ncol = 8, byrow = FALSE) # recreate data matrix
colnames(df) = c("time","open","high","low","close","vwap","colume","count")
df = df[,1:5]

if(new_date %in% df[,1]){
  id = which(df[,1] == new_date) # get new date row
  dat.origin = df[1:id,] # shorten df to include only 1 new interval
  # write out current date/time and price
  sink('current_price.txt')
  cat(as.character(dat.origin[nrow(dat.origin),1]))
  cat('\n')
  cat(dat.origin[nrow(dat.origin),5])
  cat('\n')
  sink()  
  print('New data.')
} else {
  dat.origin = df
  print('no new data')
}

########## SAR ALGO  ########## 

sar = SAR(dat.origin[,3:4], accel = c(v,v))

dat = dat.origin


buy = sell = 0
for(i in 2:nrow(dat)){
  if(dat[i-1,5] < sar[i-1] & dat[i,5] >= sar[i]){
    buy = c(buy,i)
  } else if(dat[i-1,5] > sar[i-1] & dat[i,5] <= sar[i]){
    sell = c(sell,i)
  }
}
# remove first zero
buy = buy[-1]
sell = sell[-1]

######### OUTPUT ###############

# read in trade history
trade_hist = read.csv('trade_hist.csv')
trade_hist = as.matrix(trade_hist[,-1])

# write out signal
signal = max(buy,sell)
trade = matrix(data = 0, ncol = 3, nrow = 1) # create matrix to fill with trade information
if(signal != nrow(dat)){
  trade = NA
} else if (signal %in% buy){
  trade[1,1] = as.character(dat[signal,1]) # date
  trade[1,2] = 'buy'  # signal
  trade[1,3] = dat[signal,5] # price
  trade_hist = rbind(trade_hist, trade)
  # write out new file
  write.csv(trade_hist, file = 'trade_hist.csv')
  # write out plot
  png(filename="plot.png")
  plot(x = 1:nrow(dat), y = dat[,5], type = 'l', xlab = '30-min interval', ylab = 'ETH Price', main = 'ETH Price and Historic Trades')
  lines(1:length(sar), y = sar, col = "grey")
  abline(v= buy, col = 3, lty = 2)
  abline(v = sell, col = 2, lty = 2)
  dev.off()
} else if (signal %in% sell){
  trade[1,1] = as.character(dat[signal,1]) # date
  trade[1,2] = 'sell'  # signal
  trade[1,3] = dat[signal,5] # price
  trade_hist = rbind(trade_hist, trade)
  # write out new file
  write.csv(trade_hist, file = 'trade_hist.csv')
  # write out plot
  png(filename="plot.png")
  plot(x = 1:nrow(dat), y = dat[,5], type = 'l', xlab = '30-min interval', ylab = 'ETH Price', main = 'ETH Price and Historic Trades')
  lines(1:length(sar), y = sar, col = "grey")
  abline(v= buy, col = 3, lty = 2)
  abline(v = sell, col = 2, lty = 2)
  dev.off()
}

write.csv(dat[buy,1], file = 'buy.csv')
write.csv(dat[sell,1], file = 'sell.csv')

