import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

data=yf.download(tickers=["AAPL","GOOG"],start='2019-01-01', end='2022-12-31',group_by="ticker")
df=data["AAPL"]

df["moving_avg"]=df["Close"].rolling(window=20).mean().shift(1)
df["moving_avg2"]=df["Close"].rolling(window=50).mean().shift(1)
df["r"]=df["Close"].pct_change()
distance = (df["Close"] - df["moving_avg"]) / df["moving_avg"]
threshold = 0.01

# signal: +1 (long), -1 (short), 0 (flat)
df["signal"] = np.where(distance > threshold, 1,
                  np.where(distance < -threshold, -1, 0))

df["shiftsignal"] = df["signal"].shift(1).fillna(0)
strat=df["shiftsignal"]*df["r"]
#Costs
trades = df["shiftsignal"].diff().abs()
cost = 0.001
strat_net = strat - trades * cost
#if you just held apple
df["Market_Cum"] = ((1 + df["r"]).cumprod()-1)*100
#strategy returns
df["Strategy_Cum"] = ((1 + strat_net ).cumprod()-1)*100

win_rate = (strat > 0).sum() / (strat != 0).sum()

df["volatility"] = strat.rolling(window=20).std()
df["volatility2"] = strat.rolling(window=50).std()
sharpe = strat.mean() / strat.std()* np.sqrt(252)
#For apple
df["previous_peaks"]=df["Close"].cummax()
df["drawdowns"]=(((df["Close"]-df["previous_peaks"])/df["previous_peaks"]))*100
df["maxdrawdown"]=df["drawdowns"].min()
#For strategy
stratcum=(1+strat_net).cumprod()
p_p_strat= (stratcum).cummax()
d_d_strat=(((stratcum - p_p_strat)/p_p_strat))*100
m_d_d_strat=d_d_strat.min()

figure,axes= plt.subplots(2,2)
axes[0,0].plot(df.index,df["moving_avg"],label="Moving Average")
axes[0,0].set_title("Moving Average")
axes[0,0].plot(df.index,df["moving_avg2"])
axes[0,0].plot(df.index,df["Close"])
axes[0,0].set_ylabel("Price")
axes[1,0].plot(df.index, df["Market_Cum"], label="Market")
axes[1,0].plot(df.index, df["Strategy_Cum"])
axes[1,0].set_title("Back Tester")
axes[1,0].set_xlabel("Date")
axes[1,0].set_ylabel("Returns in %")
axes[0,1].plot(df.index,df["volatility"])
axes[0,1].plot(df.index,df["volatility2"])
axes[0,1].set_title("Volatility")
axes[1,1].set_title("Drawdowns & Equity Curve")
axes[1,1].plot(df.index,df["Close"])
axes[1,1].plot(df.index,df["previous_peaks"])
axes[1,1].plot(df.index,df["drawdowns"])
axes[1,1].plot(df.index,d_d_strat)

print(sharpe,win_rate,m_d_d_strat)
plt.tight_layout()
plt.show()





