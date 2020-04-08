import streamlit as st
from src.nyt import nyt 
from src.nys import nys

datasets = {
    '-':None,
    'US County Level Data': nyt, 
    'New York State County Level Data': nys
}

def run():
    name = st.sidebar.selectbox('select data source', list(datasets.keys()), index=2)
    app = datasets[name]
    if name == '-':
        st.sidebar.success("Select a dataset above.")
        st.title('COVID-19 Explorer')

        st.header('Info about the data sources:')
        st.markdown(''' 
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
        ''', unsafe_allow_html=True)
    else:
        app()

if __name__ == "__main__":
    run()