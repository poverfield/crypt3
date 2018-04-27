# SAR Algorithm

# load packages
suppressWarnings(library(quantmod))
suppressWarnings(library(TTR))

# wait 50 seconds to run so it'll run at minutes 29:50 min and 59:50
Sys.sleep(50)

# Sar Paramaters
v = 0.031

# create dummy ohlc.out to compare lengths
ohlc.out = 1
while(length(ohlc.out) == 1){ # run until the data downloads
  # query data
  # download data from Kraken
  pair = "XETHZUSD" # 0r "XXRPZUSD"
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


# set up directory on rasbperry
dir = '/home/pi/Desktop/files'
setwd(dir)

# read in aggregate data
df_hist = read.csv('eth_data.csv')
df_hist = df_hist[,-1]

# number of new intervals (720 = 0, 719 = 1, 718 = 2... etc)
id = which(df[,1] == df_hist[nrow(df_hist),1])

if(id < 720){
  dat = rbind(df_hist, df[(id+1):nrow(df),])
  write.csv(dat, file = 'eth_data.csv')
  print(dat[nrow(dat),1] - dat[nrow(dat)-1,1])
} else {
  dat = df_hist
}


# save dat for algo
# if dat has more than 720 rows -- only use last 720 rows for algorithm
if(nrow(dat) > 1000){
  dat.origin = dat[(nrow(dat)-999):nrow(dat),]
} else {
  dat.origin = dat
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



# write out current date/time and price
sink('current_price.txt')
cat(as.character(dat[nrow(dat),1]))
cat('\n')
cat(dat[nrow(dat),5])
sink()
