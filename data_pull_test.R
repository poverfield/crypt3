# Run on the 0 and 30 minute interval

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
df_hist = read.csv('eth_data_test.csv')
df_hist = df_hist[,-1]

# number of new intervals (720 = 0, 719 = 1, 718 = 2... etc)
id = which(df[,1] == df_hist[nrow(df_hist),1])

if(id < 720){
  dat = rbind(df_hist, df[(id+1):nrow(df),])
  write.csv(dat, file = 'eth_data_test.csv')
}
