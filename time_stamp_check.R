## Run daily at 6:20 pm

# set up directory on rasbperry
dir = '/home/pi/Desktop/files'
setwd(dir)

#read in current interval from current_price.txt
current_date = read.delim('current_price.txt', header = FALSE)[1,1]

# Get current timestamp from Kraken data query
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
real_date = df[nrow(df)-1,1]
real_price = df[nrow(df)-1,5]

# if time stamps do not match up - write out interval_ALERT.csv
if(current_date != real_date){
  print('write out ALERT file')
  sink('timestamp_ALERT.txt')
  cat('Timestamps do not match:')
  cat('\n')
  cat(paste('kraken timestamp:', real_date, sep = " "))
  cat('\n')
  cat(paste('Algo time stamp:', current_date, sep = " "))
  sink()  
  # write out new timestamp to current_price.txt
  sink('current_price.txt')
  cat(as.character(real_date))
  cat('\n')
  cat(real_price)
  cat('\n')
  sink()  
  
} else{
  print('Time stamps are equal')
}

