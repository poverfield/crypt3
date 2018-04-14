# algorithm

# load packages
suppressWarnings(library(quantmod))
suppressWarnings(library(TTR))

# wait 50 seconds to run so it'll run at minutes 29.5 min and 59.5
Sys.sleep(50)

# create dummy ohlc.out to compare lengths
ohlc.out = 1
while(length(ohlc.out) == 1){ # run until the data downloads
  # query data
  # download data from Kraken
  pair = "XXBTZUSD" # 0r "XXRPZUSD"
  interval = '30'
  base.url = "https://api.kraken.com/0/public/OHLC"
  url <- paste0(base.url, "?", "pair=", pair, "&interval=", interval)
  
  
  # interval = minute
  ohlc.out <- jsonlite::fromJSON(url) 
}

# create data table
df = ohlc.out[[2]]$XXBTZUSD
df = as.numeric(df) # change to numeric
df = matrix(data = df, ncol = 8, byrow = FALSE) # recreate data matrix
colnames(df) = c("time","open","high","low","close","vwap","colume","count")
df = df[,1:5]


# set up directory on rasbperry
dir = '/home/pi/Desktop/files'
setwd(dir)

# read in aggregate data
df_hist = read.csv('xbt_data.csv')
df_hist = df_hist[,-1]

# number of new intervals (720 = 0, 719 = 1, 718 = 2... etc)
id = which(df[,1] == df_hist[nrow(df_hist),1])

if(id < 720){
  dat = rbind(df_hist, df[(id+1):nrow(df),])
  write.csv(dat, file = 'xbt_data.csv')
  print(dat[nrow(dat),1] - dat[nrow(dat)-1,1])
} else {
  dat = df_hist
}


# save dat for algo
# if dat has more than 720 rows -- only use last 720 rows for algorithm
if(nrow(dat) > 1500){
  dat.origin = dat[(nrow(dat)-1499):nrow(dat),]
} else {
  dat.origin = dat
}



# parameters: (1)n_bb, (2)n_sd, (3)n_adx, (4)sma_s, (5)sma_l, (6)adx_lim = 20, (7)take_proft
v = c(24.835600,  1.975548, 18.474961, 17.654480, 60.240259, 20.560255,  1.477374)

n_bb = as.integer(v[1]) #20
sd_bb = v[2] #2
bb = BBands(dat.origin[,3:5], n = n_bb, maType = SMA, sd = sd_bb)
bb = bb[-(1:n_bb),]

# ADX
n_adx = as.integer(v[3]) #20
adx = ADX(dat.origin[,3:5], n = n_adx) # adx
adx = adx[-(1:(2*n_adx)),] # remove nas

# sma
# if 
nf = as.integer(v[4]) #18
ns = as.integer(v[5]) #60
sma_l = SMA(dat.origin[,5], n = ns)
sma_s = SMA(dat.origin[,5], n = nf)

sma_l = sma_l[ns:nrow(dat.origin)]
sma_s = sma_s[ns:nrow(dat.origin)]


# Unify indicator lengths
new_length = min(nrow(bb),
                 nrow(adx),
                 length(sma_s),
                 length(sma_l))
dat = dat.origin[(nrow(dat.origin)- new_length + 1):nrow(dat.origin),]
bb = bb[(nrow(bb) - new_length + 1):nrow(bb),]
adx = adx[(nrow(adx) - new_length + 1):nrow(adx),]
sma_l = sma_l[(length(sma_l) - new_length + 1):length(sma_l)]
sma_s = sma_s[(length(sma_s) - new_length + 1):length(sma_s)]

# ADX signal
adx_lim = v[6] #20 # min value for trend
trade_adx = which(adx[,4] < adx_lim)

# macd
macd = sma_s - sma_l
macd_buy = macd_sell = 0
for(i in 3:nrow(dat)){
  if(macd[i-2] < macd[i-1] & macd[i-1] < macd[i]){
    macd_buy = c(macd_buy, i)
  } else if (macd[i-2] > macd[i-1] & macd[i-1] > macd[i]){
    macd_sell = c(macd_sell, i)
  }
}

# Signal
# bol. band if adx < adx_lim
buy = sell = 0
for(i in 2:nrow(dat)){
  if(dat[i-1,5] < bb[i-1,1] & dat[i,5] > bb[i,1] &  # require previous 2 bb to be testing band
     i %in% trade_adx){
    buy = c(buy,i)
  } else if(dat[i-1,5] > bb[i-1,3] & dat[i,5] < bb[i,3] & 
            i %in% trade_adx){
    sell = c(sell,i)
  }
}
bb_buy = buy[-1]
bb_sell = sell[-1]

# TRADE: place order once macd favors bb signal
buy = sell = 0
for(i in 1:length(bb_sell)){
  if(bb_sell[i] %in% macd_sell){
    sell = c(sell,bb_sell[i])
  } else {
    sell = c(sell, macd_sell[which(macd_sell > bb_sell[i])[1]])
  }
}
for(i in 1:length(bb_buy)){
  if(bb_buy[i] %in% macd_buy){
    buy = c(buy, bb_buy[i])
  } else {
    buy = c(buy, macd_buy[which(macd_buy > bb_buy[i])[1]])
  }
}
buy = buy[-1]
sell = sell[-1]

# remove NAs
buy = buy[!is.na(buy)]
sell = sell[!is.na(sell)]

# OUTPUT
trade_hist = read.csv('trade_hist.csv') # read in previous trades
trade_hist = as.matrix(trade_hist[,-1])


signal = max(buy,sell)
trade = matrix(data = 0, ncol = 3, nrow = 1) # create matrix to fill with trade information
if(signal != nrow(dat)){
  trade = NA
} else if (signal %in% buy){
  trade[1,1] = as.character(dat[signal,1]) # date
  trade[1,2] = 'buy'  # signal
  trade[1,3] = dat[signal,5] # price
  trade_hist = rbind(trade_hist, trade)
} else if (signal %in% sell){
  trade[1,1] = as.character(dat[signal,1]) # date
  trade[1,2] = 'sell'  # signal
  trade[1,3] = dat[signal,5] # price
  trade_hist = rbind(trade_hist, trade)
}

# write out new file
write.csv(trade_hist, file = 'trade_hist.csv')

# write out current date/time and price
sink('current_price.txt')
cat(as.character(dat[nrow(dat),1]))
cat('\n')
cat(dat[nrow(dat),5])
sink()
