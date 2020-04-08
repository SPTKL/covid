def nyt():
    import streamlit as st
    import pandas as pd 
    import numpy as np
    import plotly.graph_objects as go

    @st.cache(allow_output_mutation=True)
    def get_data(): 
        df_covid = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv', index_col=False)
        df_pop = pd.read_csv('https://raw.githubusercontent.com/SPTKL/covid/master/data/pop_fips.csv', index_col=False)
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

        df_covid['cases_norm'] = df_covid.cases*100000/df_covid['pop']
        df_covid['deaths_norm'] = df_covid.deaths*100000/df_covid['pop']
        df_covid['cases_norm_log10'] = np.log10(df_covid.cases_norm)
        df_covid['deaths_norm_log10'] = np.log10(df_covid.deaths_norm)
        df_covid.index = df_covid.date

        df_ny.index = df_ny.date
        df_ny = df_ny.drop('date', axis=1)
        df_ny['fat_rate'] = df_ny.deaths_norm*100/df_ny.cases_norm
        return df_covid, df_ny

    df_covid,df_ny=get_data()

    def plot_cases(df,counties, date, rolling=3, col='cases'):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.uid==i)&(df.index<=date),f'{col}_norm_log10'].rolling(rolling, center=True).mean()
            x = df.loc[(df.uid==i)&(df.index<=date),'date'].to_list()
            fig.add_trace(
                go.Scatter(
                    y=y,
                    x=x,
                    name=i,
                    mode='lines'))
        fig.add_shape(
                    type='line', 
                    xref="x",
                    yref="y",
                    x0='2020-03-16 00:00:00', x1='2020-03-16 00:00:00', 
                    y0=-2, y1=4,
                    line=dict(
                        color="lightgrey",
                        width=2,
                        dash="dot"
            )
        )
        fig.update_layout(
            template='plotly_white', 
            title=go.layout.Title(text=f'{col} Normalized by Population {rolling} Day Rolling Average'.title() ),
            xaxis=dict(title='date'),
            yaxis=dict(title=f'{col} per 100,000')
        )
        st.plotly_chart(fig)

    def plot_log_cases(df,counties, date, rolling=3, col='cases'):
        fig = go.Figure()
        for i in counties:
            L = df.loc[(df.uid==i)&(df.index<=date),f'{col}_norm'].to_list()
            y = [np.log10(y - x) for x,y in zip(L,L[1:])]
            x = [np.log10(j) for j in L]
            fig.add_trace(
                go.Scatter(
                    y=pd.Series(y).rolling(rolling, center=True).mean(),
                    x=x,
                    name=i,
                    mode='lines'))
        
        fig.update_layout(
            template='plotly_white', 
            title=go.layout.Title(text=f"{col} Growth Rate with {rolling} Day Rolling Average".title() ),
            xaxis=dict(title=f'total {col} per 100,000'), 
            yaxis=dict(title=f'{col} per day per 100,000')
        )
        
        st.plotly_chart(fig)

    def plot_log_acceleration(df,counties, date, rolling, col='cases'):
        fig = go.Figure()
        for i in counties:
            L = df.loc[(df.uid==i)&(df.index<=date),f'{col}_norm'].to_list()
            y = [np.log10(y - x) for x,y in zip(L,L[1:])]
            x = [np.log10(j) for j in L]
            slope = [(y[1]-y[0])/(x[1]-x[0]) for x,y in zip(zip(x, x[1:]), zip(y, y[1:]))]
            fig.add_trace(
                go.Scatter(
                    y=pd.Series(slope).rolling(rolling, center=True).mean(),
                    x=x,
                    name=i,
                    mode='lines'))

        fig.update_layout(
            template='plotly_white', 
            title=go.layout.Title(text=f"{col} Growth Acceleration with {rolling} Day Rolling Average".title() ),
            xaxis=dict(title=f'total {col} per 100,000'), 
            yaxis=dict(title=f'{col} per day^2 per 100,000')
        )
        
        st.plotly_chart(fig)

    df_covid['uid'] = df_covid['county'] + ', ' + df_covid['state']
    df_covid['date'] = df_covid.index
    top_counties=list(df_covid.loc[df_covid.index==df_covid.index.max(), :].sort_values('cases', ascending=False).uid)
    counties=st.sidebar.multiselect('pick your counties here', top_counties, default=top_counties[:3])
    rolling=st.sidebar.slider('pick rolling mean window', 1, 7, 3, 1)
    col=st.sidebar.selectbox('cases/deaths', ['cases', 'deaths'], index=0)
    st.write('On March 16th, Non-essential business and schools shut down')

    plot_cases(df_covid, counties, df_covid.index.max(), rolling, col)
    plot_log_cases(df_covid, counties, df_covid.index.max(), rolling, col)
    plot_log_acceleration(df_covid, counties, df_covid.index.max(), rolling, col)

    st.write(f'Data Capture Date: {df_covid.index.max()}')
    st.write(f'Data Source: https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
    st.write(f'Github repo: https://github.com/SPTKL/covid')