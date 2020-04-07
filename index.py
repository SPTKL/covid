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
        ''', unsafe_allow_html=True)
    else:
        app()

if __name__ == "__main__":
    run()