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
        dff.to_csv('../data/modzcta.csv', index=False)

if __name__ == "__main__":
    get_modzcta()