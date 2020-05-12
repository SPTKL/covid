import streamlit as st
import pandas as pd
import numpy as np
import requests
import pydeck as pdk
import geopandas as gpd
from datetime import datetime
import tempfile
import json


@st.cache(allow_output_mutation=True)
def get_data():
    data = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv",
        dtype="str",
    )
    geom = gpd.read_file(
        "https://raw.githubusercontent.com/daniel-lij/keplerTest/master/counties.json"
    )
    df = pd.merge(data, geom[["GEOID", "geometry"]], left_on="fips", right_on="GEOID")
    df = gpd.GeoDataFrame(df).set_geometry("geometry")
    return df, data.columns


df, col = get_data()
date = st.date_input("pick a date", datetime.now())
dff = df.loc[df.date == date.isoformat(), :]
dff["cases"] = dff["cases"].astype(int)
dff["deaths"] = dff["deaths"].astype(int)
temp_file = tempfile.NamedTemporaryFile(
    mode="w+", suffix=".geojson", delete=True, newline=""
)
dff.to_file(temp_file.name, driver="GeoJSON")
with open(temp_file.name) as f:
    geojson = json.load(f)

scale = (dff["cases"].max() - dff["cases"].min()) / 225
r = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=39.8283, longitude=-98.5795, zoom=3, bearing=0
    ),
    layers=[
        pdk.Layer(
            "GeoJsonLayer",
            geojson,
            opacity=0.8,
            stroked=False,
            filled=True,
            get_fill_color=f"[255, 0, properties.cases*{scale}]",
        )
    ],
)
st.pydeck_chart(r)
