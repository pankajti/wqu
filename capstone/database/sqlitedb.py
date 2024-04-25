import sqlite3
import pandas as pd
import sqlalchemy
import os

db_data_path = r'/Users/pankajti/dev/git/wqu/capstone/data/db/capstone.db'
datafiles_path = r'/Users/pankajti/dev/git/wqu/capstone/data/yf_ohlc'
con = sqlite3.connect(db_data_path)
dbEngine=sqlalchemy.create_engine(f'sqlite:///{db_data_path}')

files = os.listdir(datafiles_path)
try:
    loaded_dates =list(pd.read_sql("select date from market_data",dbEngine)['date'].unique())
except:
    loaded_dates=[]

#files=['w']

for f in files :
    market_data_path = os.path.join(datafiles_path,f)
    #market_data_path = '/Users/pankajti/dev/git/wqu/capstone/data/minute_data.csv'

    file_data = pd.read_csv(market_data_path,compression='zip')
    #file_data = pd.read_csv(market_data_path )

    file_data=file_data.rename({'Unnamed: 0':'timestamp'}, axis =1)
    file_data['date'] = file_data.timestamp.apply(lambda x:x[:10])
    file_data=file_data[~file_data.date.isin(loaded_dates)]
    if len(file_data)>100:
        file_data.to_sql(con=dbEngine, name = 'market_data', index=False, if_exists='append')
        print(f"loaded {file_data.shape} records  for {f}")
        loaded_dates.extend(file_data.date.unique())

    else:
        print(f"data already exists for {f}")
    print(f"done for {f}")

