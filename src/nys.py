def nys():
    import streamlit as st
    import pandas as pd 
    import numpy as np
    import plotly.graph_objects as go

    @st.cache(allow_output_mutation=True)
    def get_data(): 
        df_state = pd.read_csv('https://health.data.ny.gov/api/views/xdss-u53e/rows.csv')
        return df_state
    
    df_state=get_data()
    st.dataframe(df_state)