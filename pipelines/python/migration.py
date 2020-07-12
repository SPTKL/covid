import pandas as pd

df = pd.read_csv('../data/inflow.csv', usecols=['date'])

loaded_dates = list(df.date.unique())

with open('_objects.txt', 'r') as f:
    files = f.read()

all_dates = []
for i in files.split('\n'):
    if len(i) != 0:
        all_dates.append(i[45:55])

diff = [i for i in all_dates if i not in loaded_dates]

if len(diff) == 0:
    pass
else:
    for i in diff:
        s = i.split('-')
        y = s[0]
        m = s[1]
        d = s[2]
        print(f'{y}/{m}/{d}/{i}-social-distancing.csv.gz')