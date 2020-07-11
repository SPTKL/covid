import pandas as pd
import numpy as np
import requests
import sys

def get_modzcta():
     # get commit history:
        url_commits = 'https://api.github.com/repos/nychealth/coronavirus-data/commits'
        next_page=True
        page=1
        history=[]
        while next_page:
            commits = requests.get(f'{url_commits}?page={page}').json()
            if len(commits) != 0:
                for commit in commits:
                    history.append(dict(
                        sha = commit['sha'],
                        date = commit['commit']['author']['date']
                    ))
                page += 1
            else: 
                next_page=False
        
        # Get modzcta data
        modzcta=[]
        for commit in history:
            sha = commit['sha']
            date = commit['date'][:10]
            url = f'https://raw.githubusercontent.com/nychealth/coronavirus-data/{sha}/data-by-modzcta.csv'
            try:
                df = pd.read_csv(url)
                df['date'] = date
                modzcta.append(df)
                del df
            except:
                pass
        dff = pd.concat(modzcta)
        del modzcta

        dff.date=dff.date.astype('datetime64[ns]')
        dff = dff.sort_values(['date', 'MODIFIED_ZCTA'])
        dff = dff.reset_index()
        dff['pos_new'] = dff.groupby('MODIFIED_ZCTA').COVID_CASE_COUNT.diff()
        dff['total_new'] = dff.groupby('MODIFIED_ZCTA').TOTAL_COVID_TESTS.diff()
        dff['pos_rate'] = dff.pos_new/dff.total_new
        dff['pos_rate_change'] = dff.groupby('MODIFIED_ZCTA').pos_rate.diff()
        dff['death_new_norm'] = dff.groupby('MODIFIED_ZCTA').COVID_DEATH_COUNT.diff()*100000/dff.POP_DENOMINATOR
        dff['MODIFIED_ZCTA'] = dff['MODIFIED_ZCTA'].astype(int).astype(str)
        dff['zipcode'] = dff['MODIFIED_ZCTA'] + ' - ' + dff['NEIGHBORHOOD_NAME']
        dff.index=dff.date
        dff.to_csv('../data/modzcta.csv', index=False)

if __name__ == "__main__":
    get_modzcta()