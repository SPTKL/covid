def migration():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import plotly.express as px

    @st.cache(allow_output_mutation=True)
    def get_data():
        inflow = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/inflow.csv"
        )
        outflow = pd.read_csv(
            "https://raw.githubusercontent.com/SPTKL/covid/master/data/outflow.csv"
        )
        inflow.date = inflow.date.astype("datetime64")
        outflow.date = outflow.date.astype("datetime64")
        boundary_names = {
            "01": "AL",
            "02": "AK",
            "04": "AZ",
            "05": "AR",
            "06": "CA",
            "08": "CO",
            "09": "CT",
            "10": "DE",
            "12": "FL",
            "13": "GA",
            "15": "HI",
            "16": "ID",
            "17": "IL",
            "18": "IN",
            "19": "IA",
            "20": "KS",
            "21": "KY",
            "22": "LA",
            "23": "ME",
            "24": "MD",
            "25": "MA",
            "26": "MI",
            "27": "MN",
            "28": "MS",
            "29": "MO",
            "30": "MT",
            "31": "NE",
            "32": "NV",
            "33": "NH",
            "34": "NJ",
            "35": "NM",
            "36": "NY",
            "37": "NC",
            "38": "ND",
            "39": "OH",
            "40": "OK",
            "41": "OR",
            "42": "PA",
            "44": "RI",
            "45": "SC",
            "46": "SD",
            "47": "TN",
            "48": "TX",
            "49": "UT",
            "50": "VT",
            "51": "VA",
            "53": "WA",
            "54": "WV",
            "55": "WI",
            "56": "WY",
            "60": "AS",
            "66": "GU",
            "69": "MP",
            "72": "PR",
            "78": "VI",
            "11": "DC",
            "MSA": "MSA",
        }
        county_names = {
            "36061": "MN",
            "36047": "BK",
            "36005": "BX",
            "36085": "SI",
            "36081": "QN",
        }
        inflow["boundary_name"] = inflow.boundary.apply(
            lambda x: boundary_names.get(x, x)
        )
        inflow["county_name"] = inflow.desti_county.apply(
            lambda x: county_names.get(str(x), x)
        )
        outflow["boundary_name"] = outflow.boundary.apply(
            lambda x: boundary_names.get(x, x)
        )
        outflow["county_name"] = outflow.origin_county.apply(
            lambda x: county_names.get(str(x), x)
        )
        return inflow, outflow

    inflow, outflow = get_data()

    st.title("Inflow Outflow Analysis")
    county = st.selectbox(
        "pick a destination county", inflow.county_name.unique(), index=0
    )

    def inflow_plot(county):
        df = inflow.loc[inflow.county_name == county, :]
        df = df.sort_values(["county_name", "boundary", "date"])
        df["difference"] = df.groupby(
            ["county_name", "boundary"]
        ).normalized_counts.diff(364)
        rolling = 7
        fig = go.Figure()
        for i in df.boundary_name.unique():
            y = df.loc[
                (df.boundary_name == i) & (df.date >= pd.to_datetime("2020-01-01")),
                "difference",
            ]
            x = df.loc[
                (df.boundary_name == i) & (df.date >= pd.to_datetime("2020-01-01")),
                "date",
            ]
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
            title=go.layout.Title(text=f"Inflow".title()),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"2020 - 2019 difference in devices".title()),
        )
        st.plotly_chart(fig)

    inflow_plot(county)

    def outflow_plot(county):
        df = outflow.loc[outflow.county_name == county, :]
        df = df.sort_values(["county_name", "boundary", "date"])
        df["difference"] = df.groupby(
            ["county_name", "boundary"]
        ).normalized_counts.diff(364)
        rolling = 7
        fig = go.Figure()
        for i in df.boundary_name.unique():
            y = df.loc[
                (df.boundary_name == i) & (df.date >= pd.to_datetime("2020-01-01")),
                "difference",
            ]
            x = df.loc[
                (df.boundary_name == i) & (df.date >= pd.to_datetime("2020-01-01")),
                "date",
            ]
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
            title=go.layout.Title(text=f"outflow".title()),
            xaxis=dict(title="date".title()),
            yaxis=dict(title=f"2020 - 2019 difference in devices".title()),
        )
        st.plotly_chart(fig)

    outflow_plot(county)
