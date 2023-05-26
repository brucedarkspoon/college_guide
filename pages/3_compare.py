import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import yaml
import altair as alt
import os, sys, math
pd.options.mode.chained_assignment = None

st.set_page_config(layout="wide") # Set the page layout to wide

if 'app_name' not in st.session_state:
    st.session_state['app_name'] = "College Selection Guide"

# Loading the data
@st.cache_data
def load_data():
    widef = "College_Scorecard_Mobility_Latest_NonEmpty.20230524.tsv"
    tallf = "MERGED_1996_2022_ALL_NONEMPTY_TALL.SELECTED_SATCM.tsv.gz"
    yamlf = "data.yaml"
    df_wide = pd.read_csv(widef, sep="\t")
    df_tall = pd.read_csv(tallf, sep="\t", compression='gzip')
    df_tall = df_tall[df_tall['YEAR'] > 2010]
    with open(yamlf, 'r') as file:
        yaml_data = yaml.safe_load(file)
    col_dict = yaml_data['dictionary']
    ## create a dictionary to map source in col_dict to the column name and description
    ## manually add some entries
    col_dict['admissions.sat_scores.25th_percentile.overall'] = {'source': 'SATCM25', 'description': '25th percentile of SAT combined score'}
    col_dict['admissions.sat_scores.75th_percentile.overall'] = {'source': 'SATCM75', 'description': '75th percentile of SAT combined score'}
    col_dict['admissions.sat_scores.midpoint.overall'] = {'source': 'SATCMMID', 'description': 'Midpoint of SAT combined score'}
    source2col = {}
    for col in col_dict:
        d = col_dict[col]
        if 'source' in col_dict[col]:
            source2col[d['source']] = [col, d['description']]
    return df_wide, df_tall, col_dict, source2col

def update_multi_college():
    indices = df_wide[df_wide['school.name'].isin(st.session_state.multiselect_college)].index
    st.session_state.multiselected_wide = df_wide.iloc[indices]
    st.session_state.multiselected_ids = st.session_state.multiselected_wide['id']
    st.session_state.multiselected_tall = df_tall[df_tall['INSTID'].isin(st.session_state.multiselected_ids)]
    update_metric()

df_wide, df_tall, col_dict, source2col = load_data()

metrics = ['SAT_AVG', 'SATCM25', 'SATCM75', 'SATCMMID', 
           'ACTCM25', 'ACTCM75', 'ACTCMMID',
           'TUITIONFEE_IN', 'TUITIONFEE_OUT', 'TUITFTE', 
           'UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN', 'UGDS_AIAN', 'UGDS_NHPI', 
           'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN', 
           'MD_EARN_WNE_P10', 'MD_EARN_WNE_P8', 
           'MD_EARN_WNE_P6']
metric_descs = [source2col[x][1] for x in metrics]
def update_metric():
    idx = metric_descs.index(st.session_state.select_metric_desc)
    st.session_state.select_metric = metrics[idx]
#    print(st.session_state.select_metric)
#    print(st.session_state.select_metric_desc)


# Title of the application
st.title(f"{st.session_state.app_name} - Compare")

# Input to search for a University
st.markdown("#### Select multiple colleges in the dropdown menu.")
multiselect_college = st.multiselect('Select/Enter a University Name', df_wide['school.name'].unique(), key = 'multiselect_college', on_change = update_multi_college)

st.markdown("#### Select the metric you want to compare between the selected colleges.")
select_metric = st.selectbox('Select a metric', metric_descs, key = 'select_metric_desc', on_change=update_metric)

if 'multiselected_wide' in st.session_state and 'select_metric' in st.session_state:
    cur_wide = st.session_state.multiselected_wide
    cur_tall = st.session_state.multiselected_tall
    st.markdown(f"#### Comparison between the selected colleges")
    instid2name = dict(zip(cur_wide['id'], cur_wide['school.name']))
    df_compare = cur_tall[cur_tall.COLUMN == st.session_state.select_metric].replace(
                {'INSTID': instid2name}
            )
#    df_demo = df_demo[df_demo.YEAR > 2010]
    chart_compare = alt.Chart(
            df_compare
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title=st.session_state.select_metric)),
        color = alt.Color('INSTID', 
                            legend=alt.Legend(
                                title='University',
                            )),
    )
    st.altair_chart(alt.layer(chart_compare).interactive(), theme="streamlit", use_container_width=True)

# if 'selected_wide' in st.session_state:
#     cur_wide = st.session_state.selected_wide
#     cur_tall = st.session_state.selected_tall
#     st.markdown(f"## {cur_wide['school.name']}")
#     st.markdown(f"### Basic Information")
#     st.markdown(f"* A {cur_wide['tier_name'].lower()} college")
#     st.markdown(f"* Located in {cur_wide['czname']}, {cur_wide['state']}")
#     st.markdown(f"* Offers a {cur_wide['iclevel']} program.")
#     st.markdown(f"### SAT Scores by year")
#     chart_sat = alt.Chart(
#             cur_tall[cur_tall.COLUMN.isin(['SAT_AVG'])]
#         ).mark_line().encode(
#         x = alt.X('YEAR', axis=alt.Axis(format='d')),
#         y = alt.Y('VALUE', axis=alt.Axis(title='SAT Score')),
#         color = alt.Color('COLUMN', legend=alt.Legend(title='Types')),
#     )
#     st.altair_chart(alt.layer(chart_sat).interactive(), theme="streamlit", use_container_width=True)


#     st.markdown(f"### Tuitions and fees by year")
#     chart_tuition = alt.Chart(
#             cur_tall[cur_tall.COLUMN.isin(['TUITIONFEE_IN','TUITIONFEE_OUT','TUITFTE'])].replace(
#                 {'COLUMN': {'TUITIONFEE_IN': 'In-State Tuition', 
#                            'TUITIONFEE_OUT': 'Out-of-State Tuition', 
#                            'TUITFTE': 'Average Tuition / Student'}
#                 }
#             )
#         ).mark_line().encode(
#         x = alt.X('YEAR', axis=alt.Axis(format='d')),
#         y = alt.Y('VALUE', axis=alt.Axis(title='USD')),
#         color = alt.Color('COLUMN', legend=alt.Legend(title='Types')),
#     )

#     st.altair_chart(alt.layer(chart_tuition).interactive(), theme="streamlit", use_container_width=True)

#     st.markdown(f"### Demographic distribution by year")
#     df_demo = cur_tall[cur_tall.COLUMN.isin(['UGDS_WHITE','UGDS_BLACK','UGDS_HISP','UGDS_ASIAN','UGDS_AIAN','UGDS_NHPI','UGDS_2MOR','UGDS_NRA','UGDS_UNKN'])].replace(
#                 {'COLUMN': {'UGDS_WHITE':'White',
#                             'UGDS_BLACK':'Black',
#                             'UGDS_HISP':'Hispanic',
#                             'UGDS_ASIAN':'Asian',
#                             'UGDS_AIAN':'American Indian/Alaska Native',
#                             'UGDS_NHPI':'Native Hawaiian/Pacific Islander',
#                             'UGDS_2MOR':'Two or more races',
#                             'UGDS_NRA':'Non-resident aliens',
#                             'UGDS_UNKN':'Unknown'}
#                 }
#             )
#     df_demo = df_demo[df_demo.YEAR > 2010]
#     chart_demo = alt.Chart(
#             df_demo
#         ).mark_line().encode(
#         x = alt.X('YEAR', axis=alt.Axis(format='d')),
#         y = alt.Y('VALUE', axis=alt.Axis(title='Fraction')),
#         color = alt.Color('COLUMN', legend=alt.Legend(title='Race')),
#     )
#     st.altair_chart(alt.layer(chart_demo).interactive(), theme="streamlit", use_container_width=True)

#     st.markdown(f"### Median income by year")
#     df_earning = cur_tall[cur_tall.COLUMN.isin(['MD_EARN_WNE_P10','MD_EARN_WNE_P8','MD_EARN_WNE_P6','MD_EARN_WNE_1YR','MD_EARN_WNE_4YR'])].replace(
#                 {'COLUMN': {'MD_EARN_WNE_P10':'10 years after entry',
#                             'MD_EARN_WNE_P8':'8 years after entry',
#                             'MD_EARN_WNE_P6':'6 years after entry',
#                             'MD_EARN_WNE_1YR':'1 year after graduation',
#                             'MD_EARN_WNE_4YR':'4 years after graduation'}
#                 }
#             )
#     #df_earning = df_demo[df_demo.YEAR > 2010]
#     chart_earning = alt.Chart(
#             df_earning
#         ).mark_line().encode(
#         x = alt.X('YEAR', axis=alt.Axis(format='d')),
#         y = alt.Y('VALUE', axis=alt.Axis(title='USD')),
#         color = alt.Color('COLUMN', legend=alt.Legend(title='Median Income')),
#     )
#     st.altair_chart(alt.layer(chart_earning).interactive(), theme="streamlit", use_container_width=True)

#    st.dataframe(cur_tall[cur_tall.COLUMN.isin(['TUITIONFEE_IN','TUITIONFEE_OUT','TUITFTE'])])

