
# download data from Kraken
pair = "XXBTZUSD" # 0r "XXRPZUSD"
interval = '30'
base.url = "https://api.kraken.com/0/public/OHLC"
url <- paste0(base.url, "?", "pair=", pair, "&interval=", interval)
  
  
# interval = minute
ohlc.out <- jsonlite::fromJSON(url) 
  #time.stamp = ohlc.out[[2]]$last
  
# create data table + change to numerical
df = ohlc.out[[2]]$XXBTZUSD
df = as.numeric(df) # change to numeric
df = matrix(data = df, ncol = 8, byrow = FALSE) # recreate data matrix
colnames(df) = c("time","open","high","low","close","vwap","colume","count")
df = df[,1:5]

# set directory
dir = 'home/pi/Desktop/files'
setwd(dir)

# write out file
write.csv(df, file = 'xbt_data.csv')

