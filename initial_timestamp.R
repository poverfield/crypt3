# Run to create current_price.txt to use for timestamp is

# set up directory on rasbperry
dir = '/home/pi/Desktop/files'
setwd(dir)

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
dat.origin = df[,1:5]

# write out final timestamp to current_price.txt
sink('current_price.txt')
cat(as.character(dat.origin[nrow(dat.origin),1]))
cat('\n')
cat(dat.origin[nrow(dat.origin),5])
cat('\n')
sink()  

print(dat.origin[nrow(dat.origin),1])

