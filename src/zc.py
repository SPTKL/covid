def zc():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    import requests

    @st.cache(allow_output_mutation=True)
    def get_modzcta():
        dff = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/modzcta.csv",
            index_col=False,
        )
        dff.date = dff.date.astype("datetime64[ns]")
        dff = dff.sort_values(["date", "MODIFIED_ZCTA"])
        dff = dff.reset_index()
        dff["pos_new"] = dff.groupby("MODIFIED_ZCTA").COVID_CASE_COUNT.diff()
        dff["total_new"] = dff.groupby("MODIFIED_ZCTA").TOTAL_COVID_TESTS.diff()
        dff["pos_rate"] = dff.pos_new / dff.total_new
        dff["pos_rate_change"] = dff.groupby("MODIFIED_ZCTA").pos_rate.diff()
        dff["death_new_norm"] = (
            dff.groupby("MODIFIED_ZCTA").COVID_DEATH_COUNT.diff()
            * 100000
            / dff.POP_DENOMINATOR
        )
        dff["MODIFIED_ZCTA"] = dff["MODIFIED_ZCTA"].astype(int).astype(str)
        dff["zipcode"] = dff["MODIFIED_ZCTA"] + " - " + dff["NEIGHBORHOOD_NAME"]
        dff.index = dff.date
        return dff

    @st.cache(allow_output_mutation=True)
    def get_geojson():
        geojson = requests.get(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/zipcode.geojson"
        ).json()
        return geojson

    geojson = get_geojson()
    df_zc = get_modzcta()

    date = df_zc.date.max() - pd.DateOffset(1)
    top_zips = list(
        df_zc.loc[df_zc.date == df_zc.date.max(), :]
        .sort_values("pos_rate", ascending=False)
        .zipcode.unique()
    )
    zipcode = st.sidebar.multiselect(
        "pick your zipcodes here", top_zips, default=top_zips[:10]
    )
    rolling = st.sidebar.slider("pick rolling mean window", 1, 14, 3, 1)
    st.sidebar.info(f"Last Updated: {str(df_zc.date.max())[:10]}")

    def plot_1(df, date, zipcode, rolling):
        fig = go.Figure()
        for i in zipcode:
            dff = df.loc[(df.zipcode == i) & (df.date <= date) & (df.total_new > 0), :]
            y = dff.loc[:, "pos_rate"].rolling(rolling, center=True).mean()
            fig.add_trace(go.Scatter(y=y, x=dff.index, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Positivity Rate of Cumulative Tests ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    def plot_2(df, date, zipcode, rolling):
        fig = go.Figure()
        for i in zipcode:
            dff = df.loc[
                (df.zipcode == i)
                & (df.date <= date)
                & (df.date != pd.to_datetime("2020-06-30")),
                :,
            ]
            y = dff.loc[:, "death_new_norm"].rolling(rolling, center=True).mean()
            fig.add_trace(go.Scatter(y=y, x=dff.index, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Deaths normalized by population ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"normalized Deaths per 100,000".title()),
        )
        st.plotly_chart(fig)

    def plot_3(df, date, zipcode, rolling):
        fig = go.Figure()
        for i in zipcode:
            dff = df.loc[(df.zipcode == i) & (df.date <= date) & (df.total_new > 0), :]
            y = dff.loc[:, "pos_rate_change"].rolling(rolling, center=True).mean()
            fig.add_trace(go.Scatter(y=y, x=dff.index, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Change in Positivity Rate ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Positivity Rate growth rate".title()),
        )
        st.plotly_chart(fig)

    def create_map(date):
        df = df_zc.loc[(df_zc.date == date), :]
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson,
            locations="MODIFIED_ZCTA",
            featureidkey="properties.ZIPCODE",
            color="pos_rate",
            color_continuous_scale="YlOrRd",
            mapbox_style="carto-positron",
            range_color=(df.pos_rate.min(), df.pos_rate.max()),
            zoom=9,
            center={"lat": 40.7128, "lon": -74.0060},
            opacity=0.7,
            hover_name="NEIGHBORHOOD_NAME",
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)

    st.title("Zipcode Level Testing and Death Data")
    plot_1(df_zc, date, zipcode, rolling)
    plot_3(df_zc, date, zipcode, rolling)
    plot_2(df_zc, date, zipcode, rolling)

    st.header(f"Positivity Rate of {str(date)[:10]}")
    create_map(date)
