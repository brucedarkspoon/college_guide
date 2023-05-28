import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import yaml
import altair as alt
import os, sys, math
import college_guide_shared as cgs

pd.options.mode.chained_assignment = None

st.set_page_config(layout="wide") # Set the page layout to wide

## load the data just onces
df_wide, df_wide_pct, df_tall = cgs.load_data()

def update_multi_college():
    indices = df_wide[df_wide['name'].isin(st.session_state.multiselect_college)].index
    st.session_state.multiselected_wide = df_wide.iloc[indices]
    st.session_state.multiselected_ids = st.session_state.multiselected_wide['id']
    st.session_state.multiselected_tall = df_tall[df_tall['INSTID'].isin(st.session_state.multiselected_ids)]
    #indices = st.session_state.df_wide[st.session_state.df_wide['name'].isin(st.session_state.multiselect_college)].index
    #st.session_state.multiselected_wide = st.session_state.df_wide.iloc[indices]
    #st.session_state.multiselected_ids = st.session_state.multiselected_wide['id']
    #st.session_state.multiselected_tall = st.session_state.df_tall[st.session_state.df_tall['INSTID'].isin(st.session_state.multiselected_ids)]
    update_metric()

metrics = list(cgs.lts.keys())
metric_descs = list(cgs.lts.values())
def update_metric():
    idx = metric_descs.index(st.session_state.select_metric_desc)
    st.session_state.select_metric = metrics[idx]

# Title of the application
st.title(f"{cgs.app_name} - Compare")

# Input to search for a University
col1, col2 = st.columns([1, 1])
with col1:
    col1.markdown("#### Select multiple colleges to compare.")
with col2:
    expander = col2.expander("See explanation")
    expander.markdown("* Select multiple college names in the dropdown menu below.")
    expander.markdown("* Next, select the metric to compare between the colleges.")
    expander.markdown("* Chart will show the comparison between selected colleges on the selected metric.")

#multiselect_college = st.multiselect('Select/Enter a University Name', st.session_state.df_wide['name'].unique(), key = 'multiselect_college', on_change = update_multi_college)
multiselect_college = st.multiselect('Select/Enter a University Name', df_wide['name'].unique(), key = 'multiselect_college', on_change = update_multi_college)

st.markdown("#### Select the metric you want to compare between the selected colleges.")
select_metric = st.selectbox('Select a metric', metric_descs, key = 'select_metric_desc', on_change=update_metric)

if 'multiselected_wide' in st.session_state and 'select_metric' in st.session_state:
    cur_wide = st.session_state.multiselected_wide
    cur_tall = st.session_state.multiselected_tall

    ex_comp = st.expander(f"Hide/show Chart", expanded=True)

    ex_comp.markdown(f"#### Comparison between the selected colleges for: {st.session_state.select_metric_desc}")
    instid2name = dict(zip(cur_wide['id'], cur_wide['name']))
    df_compare = cur_tall[cur_tall.COLUMN == st.session_state.select_metric].replace(
                {'INSTID': instid2name}
            )
    chart_compare = alt.Chart(
            df_compare
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title=st.session_state.select_metric)),
        color = alt.Color('INSTID', 
                            legend=alt.Legend(
                                title='University',
                                labelLimit=500
                            )),
    )
    ex_comp.altair_chart(alt.layer(chart_compare).interactive(), theme="streamlit", use_container_width=True)
