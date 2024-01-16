import eia
import pandas as pd
import requests
import numpy as np
# the API key we recieved from EIA
# Initiates a session with the EIA datacenter to recieve datasets
eia_key = r'KhUGeRcdKwP8WpygPCSDasWyaRburTqyE9er7aUN'

eia_api = eia.API(eia_key)
series='STEO.COPR_OPEC.M'
url_data = 'http://api.eia.gov/v2/seriesid/{}?api_key={}&out=json'
values_dict = {}
search = requests.get(url_data.format(series, eia_key))
eia_data = pd.DataFrame(search.json().get('response').get('data'))
eia_data=eia_data.set_index('period')
import datetime # Using the datetime library
def convert_to_datetime(input):
    return datetime.datetime.strptime(input[:9], "%Y-%m").date();
# Apply to entire index
eia_data.index = eia_data.index.map(convert_to_datetime);
# Convert dataframe index to datetime64[ns] index
eia_data.index = pd.to_datetime(eia_data.index);
eia_data= eia_data[['value']]
# pgmpy stores the column names as the variable name
eia_data.columns = ['TOTAL.COEXPUS.M'];
eia_data.replace('-', np.nan, regex=True, inplace=True);
eia_data.replace('No Data Reported', np.nan, regex=True, inplace=True);
eia_data.loc[eia_data['TOTAL.COEXPUS.M']=='No Data Reported']=np.NAN
# Backward fill the holes, by filling them with the data infront.
eia_data.fillna(method='bfill', inplace=True);


def clean_EIA(data):
    data.replace('-', np.nan, regex=True, inplace=True);
    data.fillna(method='bfill', inplace=True);
    data.index = data.index.map(convert_to_datetime);
    data.index = pd.to_datetime(data.index);
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(20,6));
ax.plot(eia_data)
plt.show()

print(eia_data)