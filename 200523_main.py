import time

import requests
from bs4 import BeautifulSoup
import pandas_datareader.data as web
import pandas as pd
import datetime
import matplotlib.pyplot as plt

def get_code(table, firm):
     code = table[table["name"]==firm]["code"].values[0]
     return "{:06d}".format(int(code))

df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', header=0)[0]

df = df[['회사명', '종목코드']]
df = df.rename(columns={'회사명': 'name', '종목코드': 'code'})

#print(df)
codename = get_code(df, "삼성전자")
codename = codename + ".KS"

start = datetime.datetime(2016, 3, 1)
end = datetime.datetime(2020, 3, 11)

gs = web.DataReader(codename, "yahoo", start, end)

gs = gs["Close"]
print(gs.tail())

plt.plot(gs)
plt.show()