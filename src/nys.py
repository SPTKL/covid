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

        df_state_['pos_total_norm'] = df_state_.pos_total/df_state_['tests_total']*100
        # df_state_['pos_new_norm'] = df_state_.pos_new/df_state_['tests_total']*100

        df_state_.test_date = df_state_.test_date.astype('datetime64[ns]')
        df_state_.index = df_state_.test_date
        return df_state_
    
    df_state =get_data()
    df_state = df_state.sort_index()
    date=df_state.index.max()
    top_counties=list(df_state.loc[(df_state.index==df_state.index.max())&(df_state.tests_total >= 10000), :].sort_values('pos_total_norm', ascending=False).county)
    
    counties=st.sidebar.multiselect('pick your counties here', top_counties, default=top_counties[:10])

    def plot_1(df,counties, date):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.county==i)&(df.index<=date), 'pos_total_norm']
            x = df.loc[(df.county==i)&(df.index<=date), 'test_date']
            fig.add_trace(
                go.Scatter(
                    y=y,
                    x=x,
                    name=i,
                    mode='lines'))

        fig.update_layout(
            template='plotly_white', 
            title=go.layout.Title(
                text='Confirmed cases normalized by population and testing capacity'.title()
                ),
            xaxis=dict(title='date'.title()),
            yaxis=dict(title=f'Percetage of positive cases per 100k Resident'.title())
        )
        st.plotly_chart(fig)
    
    def plot_2(df,counties, date):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.tests_total >= 1000)&(df.county==i), 'pos_new']
            x = df.loc[(df.tests_total >= 1000)&(df.county==i), 'pos_total']
            fig.add_trace(
                go.Scatter(
                    y=np.log10(y),
                    x=np.log10(x),
                    name=i,
                    mode='lines'))

        fig.update_layout(
            template='plotly_white', 
            title=go.layout.Title(
                text='Positive case growth rate'.title()
                ),
            xaxis=dict(title='positive total'.title()),
            yaxis=dict(title=f'positive new'.title())
        )
        st.plotly_chart(fig)

    plot_1(df_state,counties, date)
    plot_2(df_state,counties, date)