def nys():
    import streamlit as st
    import pandas as pd 
    import numpy as np
    import plotly.graph_objects as go

    @st.cache(allow_output_mutation=True)
    def get_data(): 
        df_state = pd.read_csv('https://health.data.ny.gov/api/views/xdss-u53e/rows.csv')
        fips_lookup = pd.read_csv('https://raw.githubusercontent.com/SPTKL/covid/master/data/ny_county_fips_lookup.csv')
        df_pop = pd.read_csv('https://raw.githubusercontent.com/SPTKL/covid/master/data/pop_fips.csv')
        pop = fips_lookup.merge(df_pop, how='left', left_on='County FIPS', right_on='fips')
        pop = pop[['County Name', 'pop']]
        df_state_ = df_state.merge(pop, how='left', left_on='County', right_on='County Name')
        df_state_ = df_state_.drop(columns=['County Name'])
        df_state_.columns = ['test_date', 'county', 'pos_new', 'pos_total','tests_new', 'tests_total', 'pop']
        df_state_['pos_new_norm'] = df_state_.pos_new*10000/df_state_['pop']
        df_state_['pos_total_norm'] = df_state_.pos_total*10000/df_state_['pop']
        df_state_['test_new_norm'] = df_state_.tests_new*10000/df_state_['pop']
        df_state_['tests_total_norm'] = df_state_.tests_total*10000/df_state_['pop']

        df_state_.test_date = df_state_.test_date.astype('datetime64[ns]')
        df_state_.index = df_state_.test_date
        return df_state_
    
    df_state =get_data()
    st.dataframe(df_state.head())
    date=df_state.index.max()
    top_counties=list(df_state.loc[df_state.index==df_state.index.max(), :].sort_values('pos_new', ascending=False).county)
    counties=st.sidebar.multiselect('pick your counties here', top_counties, default=top_counties[:3])
    rolling=st.sidebar.slider('pick rolling mean window', 1, 7, 3, 1)
    col=st.sidebar.selectbox('cases/deaths', ['cases', 'deaths'], index=0)
    st.write('On March 16th, Non-essential business and schools shut down')

    def plot_cases(df,counties, date):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.county==i)&(df.index<=date), 'tests_total_norm']
            x = df.loc[(df.county==i)&(df.index<=date), 'test_date']
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
        # fig.update_layout(
        #     template='plotly_white', 
        #     title=go.layout.Title(text=f'{col} Normalized by Population {rolling} Day Rolling Average'.title() ),
        #     xaxis=dict(title='date'),
        #     yaxis=dict(title=f'{col} per 100,000')
        # )
        st.plotly_chart(fig)

    plot_cases(df_state,counties, date)