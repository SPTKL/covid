import streamlit as st
import pandas as pd 
import numpy as np
import plotly.graph_objects as go
import time

@st.cache(allow_output_mutation=True)
def get_data(): 
    df_covid = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv', index_col=False)
    df_pop = pd.read_csv('https://raw.githubusercontent.com/SPTKL/covid/master/pop_fips.csv', index_col=False)
    df_covid.fips = df_covid.fips.apply(lambda x: np.nan_to_num(x))
    df_covid['fips'] = df_covid['fips'].apply(lambda x: str(int(x)))
    df_pop['fips'] = df_pop['fips'].astype(int).astype(str)
    l=[]
    for i in range(len(df_covid)):
        if df_covid.county[i]=='New York City':
            l.append('360')
        else:
            l.append(df_covid.fips[i])
    df_covid.fips = l
    df_covid.date = df_covid.date.astype('datetime64[ns]')
    df_covid = df_covid.merge(df_pop, how='left', on=['fips'])
    l=[]
    for i in range(len(df_covid)):
        if (df_covid.date[i]>pd.to_datetime('2020-03-18'))&(df_covid.deaths[i]>0)&(df_covid.county[i]=='New York City'):
            l.append(df_covid.deaths[i]/0.015)
        elif (df_covid.date[i]>pd.to_datetime('2020-03-18'))&(df_covid.deaths[i]>0)&(df_covid.county[i]!='New York City')&\
            (df_covid.state[i]=='New York')&(df_covid.county[i]!='Westchester'):
            l.append(df_covid.deaths[i]/0.025)
        else:
            l.append(df_covid.cases[i])
    df_covid['cases']=l

    df_ny = df_covid[(df_covid.state=='New York')|(df_covid.state=='New Jersey')|\
                (df_covid.state=='Connecticut')|(df_covid.state=='Pennsylvania')|\
                (df_covid.state=='Massachusetts')].reset_index().drop('index', axis=1)
    df_ny = df_ny.dropna(subset=['pop'], axis=0)
    ny_counties = list(df_ny[df_ny.date==df_ny.date.max()].sort_values('cases', ascending=False).county)
    ny_states = list(df_ny[df_ny.date==df_ny.date.max()].sort_values('cases', ascending=False).state)
    df_ny['cases_norm'] = df_ny.cases*100000/df_ny['pop']
    df_ny['deaths_norm'] = df_ny.deaths*100000/df_ny['pop']
    df_ny['cases_norm_log10'] = np.log10(df_ny.cases_norm)
    df_ny['deaths_norm_log10'] = np.log10(df_ny.deaths_norm)
    df_ny.index = df_ny.date
    df_ny = df_ny.drop('date', axis=1)
    df_ny['fat_rate'] = df_ny.deaths_norm*100/df_ny.cases_norm
    return df_covid, df_ny

df_covid,df_ny=get_data()

st.write(df_ny.index.max())
# x : cases_norm_log10
# y : changes in cases_norm_log10
def plot_log_cases(df,counties, date):
    data = []
    frames = []
    for i in counties:
        L = df.loc[(df.uid==i)&(df.index<=date),'cases_norm'].to_list()
        L_delta = [np.log10(y - x) for x,y in zip(L,L[1:])]
        data.append( 
            go.Scatter(
                y=L_delta,
                x=[np.log10(j) for j in L],
                name=i,
                mode='lines'))
    for j in df.date.unique():
        data = []
        for i in counties:
            L = df.loc[(df.uid==i)&(df.index<=j),'cases_norm'].to_list()
            L_delta = [np.log10(y - x) for x,y in zip(L,L[1:])]
            data.append(go.Scatter(
                        y=L_delta,
                        x=[np.log10(j) for j in L],
                        name=i,
                        mode='lines'))
        frames.append(go.Frame(data=data))

    fig = go.Figure(
        data=data,
        layout=go.Layout(
                updatemenus=[dict(type="buttons",
                    buttons=[dict(label="Play",
                    method="animate",
                    args=[None])])]),
        frames=frames
    )
    st.plotly_chart(fig)

df_ny['uid'] = df_ny['county'] + ' ,' + df_ny['state']
df_ny['date'] = df_ny.index
top_counties=list(df_ny.loc[df_ny.index==df_ny.index.max(), :].sort_values('cases', ascending=False).uid)[:10]
counties=st.multiselect('pick your counties here', top_counties, default=top_counties[:3])
plot_log_cases(df_ny, counties, df_ny.index.max())