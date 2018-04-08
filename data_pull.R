# pull data and aggregate every 30 minutes

# query data from Kraken
pair = "XXBTZUSD" # 0r "XXRPZUSD"
base.url = "https://api.kraken.com/0/public/OHLC"
url <- paste0(base.url, "?", "pair=", pair)

# interval = minute
ohlc.out <- jsonlite::fromJSON(url) 
#time.stamp = ohlc.out[[2]]$last

# create data table + change to numerical
df = ohlc.out[[2]]$XXBTZUSD
df = as.numeric(df) # change to numeric
df = matrix(data = df, ncol = 8, byrow = FALSE) # recreate data matrix
colnames(df) = c("time","open","high","low","close","vwap","colume","count")
df = df[,1:5]


# read in aggregate data
df_hist = read.csv('xbt_data.csv')
df_hist = df_hist[,-1]

# if more than 30 1-minute intervals available--> add to df_hist
# use 28 instead of 29 to allow errow window in data pull (no use for open price in algo)
if(length(which(df[,1] > df_hist[nrow(df_hist),1])) > 28 &
   length(which(df[,1] > df_hist[nrow(df_hist),1])) != 720){
  new_dat = c(df[nrow(df),1], 
              df[nrow(df)-28,2], 
              max(df[(nrow(df)-28):nrow(df),3]), 
              min(df[(nrow(df)-28):nrow(df),4]),
              df[nrow(df), 5])
  dat = rbind(df_hist, new_dat)
  write.csv(dat, file = 'xbt_data.csv')
} else {
  dat = df_hist # keep script running without newest interval
}
