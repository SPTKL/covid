def zc():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px
    import requests

    @st.cache(allow_output_mutation=True)
    def get_data():
        df_zc = pd.read_csv(
            "https://raw.githubusercontent.com/chazeon/NYState-COVID-19-Tracker/master/data/NYC-github-coronavirus-data-tests-by-zcta.csv"
        )
        df_zc_pop = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/pop_zipcode.csv"
        )
        geojson = requests.get(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/zipcode.geojson"
        ).json()
        df_zc = df_zc.dropna(subset=["zip_code", "uhf_code"], axis=0)
        df_zc = df_zc.reset_index().drop("index", axis=1)
        nta_col = list(df_zc.columns[6:])
        l = []
        for i in range(0, len(df_zc), 2):
            for j in nta_col:
                l.append(
                    [
                        j,
                        df_zc.zip_code[i],
                        df_zc.uhf_name[i],
                        list(
                            df_zc[
                                (df_zc.zip_code == df_zc.zip_code[i])
                                & (df_zc.status == "Positive")
                            ][j]
                        )[0],
                        list(
                            df_zc[
                                (df_zc.zip_code == df_zc.zip_code[i])
                                & (df_zc.status == "Total")
                            ][j]
                        )[0],
                    ]
                )
        df_zc = pd.DataFrame(
            l, columns=["date", "zipcode", "name", "positive", "total"]
        )
        df_zc = df_zc.loc[df_zc.date != '2020-04-26', :]
        df_zc.date = df_zc.date.apply(lambda x: x.replace('2020-05-19.1', '2020-05-20'))
        df_zc_pop = df_zc_pop.groupby("zipcode")["population"].sum().reset_index()
        df_zc = df_zc.merge(
            df_zc_pop[df_zc_pop.population != 0][["zipcode", "population"]],
            on="zipcode",
            how="left",
        )
        df_zc.date = df_zc.date.astype("datetime64[ns]")
        df_zc.index = df_zc.date
        df_zc = df_zc.drop("date", axis=1)
        df_zc["confidence_int"] = 1 - np.sqrt(1 / df_zc.total - 1 / df_zc.population)
        df_zc["ratio"] = df_zc.positive / df_zc.total
        df_zc["zip"] = df_zc["zipcode"].astype(int).astype(str)
        df_zc["zipcode"] = (
            df_zc["zipcode"].astype(int).astype(str) + " " + df_zc["name"]
        )
        return df_zc, geojson

    df_zc, geojson = get_data()
    date = df_zc.index.max()
    top_zips = list(
        df_zc.loc[df_zc.index == df_zc.index.max(), :]
        .sort_values("ratio", ascending=False)
        .zipcode
    )
    zipcode = st.sidebar.multiselect(
        "pick your zipcodes here", top_zips, default=top_zips[:5]
    )
    rolling = st.sidebar.slider("pick rolling mean window", 1, 14, 3, 1)
    st.sidebar.info(
        """
    
    **Positivity Rate of Cumulative Tests** = Total positive cases / Total tests performed

    **Positivity Rate of Daily Tests** = Daily New positive cases / Daily New tests performed

    """
    )
    st.sidebar.warning('Note that Apirl 26, 2020 data is removed because it\'s likely an anosmaly')

    def create_map(date):
        df = df_zc.loc[df_zc.index == date, :]
        fig = px.choropleth_mapbox(
            df,
            geojson=geojson,
            locations="zip",
            featureidkey="properties.ZIPCODE",
            color="ratio",
            color_continuous_scale="YlOrRd",
            range_color=(df.ratio.min(), df.ratio.max()),
            mapbox_style="carto-positron",
            zoom=9,
            center={"lat": 40.7128, "lon": -74.0060},
            opacity=0.7,
            hover_name="name",
        )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig)

    def plot_1(df, date, zipcode, rolling):
        fig = go.Figure()
        for i in zipcode:
            y = (
                df.loc[(df.zipcode == i) & (df.index <= date), "ratio"]
                .rolling(rolling, center=True)
                .mean()
            )
            fig.add_trace(go.Scatter(y=y, x=df.index, name=i, mode="lines"))

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
            pos = df.loc[(df.zipcode == i) & (df.index <= date), "positive"]
            tot = df.loc[(df.zipcode == i) & (df.index <= date), "total"]
            pos_new = [y2 - y1 for y1, y2 in zip(pos, pos[1:])]
            tot_new = [y2 - y1 for y1, y2 in zip(tot, tot[1:])]
            y = [p / t if t!=0 else np.nan for p, t in zip(pos_new, tot_new)]

            y = (
                pd.Series(y)
                .rolling(rolling, center=True)
                .mean()
            )
            fig.add_trace(go.Scatter(y=y, x=df.index, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Positivity Rate of Daily tests ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    def plot_3(df, date, zipcode, rolling):
        fig = go.Figure()
        for i in zipcode:
            pos = df.loc[(df.zipcode == i) & (df.index <= date), "positive"]
            tot = df.loc[(df.zipcode == i) & (df.index <= date), "total"]
            pos_new = [y2 - y1 for y1, y2 in zip(pos, pos[1:])]
            tot_new = [y2 - y1 for y1, y2 in zip(tot, tot[1:])]
            y = [p / t if t!=0 else np.nan for p, t in zip(pos_new, tot_new)]
            y = [y2 - y1 for y1, y2 in zip(y, y[1:])]
            y = (
                pd.Series(y)
                .rolling(rolling, center=True)
                .mean()
                .rolling(rolling, center=True)
                .mean()
            )
            fig.add_trace(go.Scatter(y=y, x=df.index, name=i, mode="lines"))

        fig.update_layout(
            template="plotly_white",
            title=go.layout.Title(
                text=f"Changes in Positivity Rate of Daily Tests ({rolling} day rolling mean)".title()
            ),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"Changes in Positivity Rate".title()),
        )
        st.plotly_chart(fig)

    plot_1(df_zc, date, zipcode, rolling)
    plot_2(df_zc, date, zipcode, rolling)
    plot_3(df_zc, date, zipcode, rolling)

    st.header("Positivity Rate of Cumulative Tests")
    create_map(date)