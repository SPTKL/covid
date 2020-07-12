import streamlit as st
from src.nyt import nyt
from src.nys import nys
from src.zc import zc
from src.migration import migration

datasets = {
    "-": None,
    "US County Level Data": nyt,
    "New York State County Level Data": nys,
    "Zipcode Level Data": zc,
    "Inflow Outflow": migration,
}


def run():
    name = st.sidebar.selectbox("select data source", list(datasets.keys()), index=0)
    app = datasets[name]
    if name == "-":
        st.sidebar.success("Select a dataset above.")
        st.title("COVID-19 Explorer")

        st.header("Info about the data sources:")
        st.markdown(
            """ 
        + New York State testing data is published on NYS OpenData [(link)](https://health.data.ny.gov/Health/New-York-State-Statewide-COVID-19-Testing/xdss-u53e)
        + US County Level Data is from New York Times Github Repo [(link)](https://github.com/nytimes/covid-19-data)
        + county level population data is pulled from acs 2018, run the code below to pull the data:
        ```python
        import requests
        import json
        url='https://api.census.gov/data/2018/acs/acs5?get=NAME,group(B01001)&for=county:*'
        resp = requests.request('GET', url).content
        df = pd.DataFrame(json.loads(resp)[1:])
        df.columns = json.loads(resp)[0]
        df = df[['NAME', 'GEO_ID', 'B01001_001E']]
        df['fips'] = df['GEO_ID'].apply(lambda x: x[-5:])
        df['pop'] = df['B01001_001E']
        df[['fips', 'pop']].to_csv('pop_fips.csv', index=False)
        ```
        + Zipcode level testing data is scraped from dohmh github repo [(link)](https://github.com/nychealth/coronavirus-data)
        + Zipcode boundry is from NYC OpenData, which also contains population estimates [(link)](https://data.cityofnewyork.us/Business/Zip-Code-Boundaries/i8iw-xf4u/data?no_mobile=true)
        ```python
        import requests
        import pandas as pd

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
        ```
        """,
            unsafe_allow_html=True,
        )
    else:
        app()


if __name__ == "__main__":
    run()
