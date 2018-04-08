
# ***Only run once to create aggregate data



# download data from Kraken
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

dat = matrix(data = NA, ncol = 5, nrow = 24) 
colnames(dat) = c('close_time','open','high','low','close')
for(i in 1:nrow(dat)){
  dat[i,1] = df[30*i,1]
  dat[i,2] = df[(30*(i-1)+1),2]
  dat[i,3] = max(df[(30*(i-1)+1):(30*i),3])
  dat[i,4] = min(df[(30*(i-1)+1):(30*i),4])
  dat[i,5] = df[30*i,5]
}

write.csv(dat, file = 'xbt_hist_data.csv')



