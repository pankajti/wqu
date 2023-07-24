import pandas as pd
import os

data_files_path = r'/Users/shritiwari/dev/git/finance/data'
files = os.listdir(data_files_path)

df = pd.concat([pd.read_csv(os.path.join(data_files_path, p) ) for p in files if p.endswith(".csv") ])

print("aa")


