def nys():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go

    @st.cache(allow_output_mutation=True)
    def get_data():
        df_state = pd.read_csv(
            "https://health.data.ny.gov/api/views/xdss-u53e/rows.csv"
        )
        fips_lookup = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/ny_county_fips_lookup.csv"
        )
        df_pop = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/pop_fips.csv"
        )
        pop = fips_lookup.merge(
            df_pop, how="left", left_on="County FIPS", right_on="fips"
        )
        pop = pop[["County Name", "pop"]]
        df_state_ = df_state.merge(
            pop, how="left", left_on="County", right_on="County Name"
        )
        df_state_ = df_state_.drop(columns=["County Name"])
        df_state_.columns = [
            "test_date",
            "county",
            "pos_new",
            "pos_total",
            "tests_new",
            "tests_total",
            "pop",
        ]

        df_state_["pos_total_norm"] = (
            df_state_.pos_total / df_state_["tests_total"] * 100
        )
        df_state_["pos_total_norm_pop"] = (
            df_state_.pos_total / df_state_["pop"] * 100000
        )
        df_state_["pos_new_norm_pop"] = df_state_.pos_new / df_state_["pop"] * 100000
        df_state_["pos_new_norm"] = df_state_.pos_new / df_state_["tests_new"] * 100
        df_state_["tests_total_norm"] = (
            df_state_.tests_total / df_state_["pop"] * 100000
        )
        df_state_["tests_new_norm"] = df_state_.tests_new / df_state_["pop"] * 100000

        df_state_.test_date = df_state_.test_date.astype("datetime64[ns]")
        df_state_.index = df_state_.test_date
        return df_state_

    df_state = get_data()
    df_state = df_state.sort_index()
    date = df_state.index.max()
    top_counties = list(
        df_state.loc[
            (df_state.index == df_state.index.max()) & (df_state.tests_total >= 1000), :
        ]
        .sort_values("pos_total_norm", ascending=False)
        .county
    )

    counties = st.sidebar.multiselect(
        "pick your counties here", top_counties, default=top_counties[:5]
    )
    rolling = st.sidebar.slider("pick rolling mean window", 1, 28, 3, 1)

    st.sidebar.info(
        """
    
    **Positivity Rate of Cumulative Tests** = Total positive cases / Total tests performed

    **Positivity Rate of Daily Tests** = Daily New positive cases / Daily New tests performed

    """
    )

    st.title("New York State Testing Data")

    def plot_0(df, counties, date, rolling):
        fig = go.Figure()
        for i in counties:
            y = (
                df.loc[(df.county == i) & (df.index <= date), "tests_new_norm"]
                .rolling(rolling, center=True)
                .mean()
            )
            x = df.loc[(df.county == i) & (df.index <= date), "test_date"]
            fig.add_trace(go.Scatter(y=y, x=x, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"testing capacity ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"test per day per 100,000".title()),
        )
        st.plotly_chart(fig)

    def plot_1(df, counties, date, rolling):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.county == i) & (df.index <= date), "pos_total_norm"]
            x = df.loc[(df.county == i) & (df.index <= date), "test_date"]
            fig.add_trace(
                go.Scatter(
                    y=pd.Series(y).rolling(rolling, center=True).mean(),
                    x=x,
                    name=i,
                    mode="lines",
                )
            )

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Positivity Rate of Cumulative tests ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    def plot_3(df, counties, date, rolling):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.county == i) & (df.index <= date), "pos_new_norm"]
            x = df.loc[(df.county == i) & (df.index <= date), "test_date"]
            fig.add_trace(
                go.Scatter(
                    y=pd.Series(y).rolling(rolling, center=True).mean(),
                    x=x,
                    name=i,
                    mode="lines",
                )
            )

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Positivity Rate of Daily Tests ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    def plot_2(df, counties, date, rolling):
        fig = go.Figure()
        for i in counties:
            y = df.loc[(df.county == i) & (df.index <= date), "pos_new_norm"]
            x = df.loc[(df.county == i) & (df.index <= date), "test_date"]
            y = [y2 - y1 for y1, y2 in zip(y, y[1:])]
            fig.add_trace(
                go.Scatter(
                    y=pd.Series(y).rolling(rolling, center=True).mean(),
                    x=x,
                    name=i,
                    mode="lines",
                )
            )

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Change in Daily Positivity Rate ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Change in Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    plot_0(df_state, counties, date, rolling)
    plot_1(df_state, counties, date, rolling)
    plot_3(df_state, counties, date, rolling)
    plot_2(df_state, counties, date, rolling)
