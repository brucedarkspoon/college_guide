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
    df_wide_pct = df_wide.rank(pct=True) * 100

    df_tall = pd.read_csv(tallf, sep="\t", compression='gzip')
    with open(yamlf, 'r') as file:
        yaml_data = yaml.safe_load(file)
    col_dict = yaml_data['dictionary']
    return df_wide, df_wide_pct, df_tall, col_dict

def update_college():
    idx = df_wide[df_wide['school.name'] == st.session_state.select_college].index[0]
    st.session_state.selected_wide = df_wide.iloc[idx]
    st.session_state.selected_pct = df_wide_pct.iloc[idx]
    st.session_state.selected_id = st.session_state.selected_wide['id']
    st.session_state.selected_tall = df_tall[df_tall['INSTID'] == st.session_state.selected_id]

df_wide, df_wide_pct, df_tall, col_dict = load_data()

# Title of the application
st.title(f"{st.session_state.app_name} - View")

# Input to search for a University
st.markdown("#### Select or search for a college in the dropdown menu.")
select_college = st.selectbox('Select/Enter a University Name', df_wide['school.name'].unique(), key = 'select_college', on_change = update_college)

if 'selected_wide' in st.session_state:
    cur_wide = st.session_state.selected_wide
    cur_tall = st.session_state.selected_tall
#    st.markdown(f"## {cur_wide['school.name']}")
#    st.markdown(f"### Basic Information")
#    st.markdown(f"* A {cur_wide['tier_name'].lower()} college")
#    st.markdown(f"* Located in {cur_wide['czname']}, {cur_wide['state']}")
#    st.markdown(f"* Offers a {cur_wide['iclevel']} program.")

    st.markdown(f"#### You selected : {st.session_state.select_college}")
    st.markdown(f"##### Basic Information of {st.session_state.select_college}")
    st.markdown(f"* A ***{cur_wide['tier_name'].lower()}*** college")
    st.markdown(f"* Located in ***{cur_wide['czname']}, {cur_wide['state']}***")
    st.markdown(f"* Offers a ***{cur_wide['iclevel']}*** program.")
    st.markdown(f"* The size of student cohort is ***{cur_wide['count']:.0f}*** per year.")
    st.markdown(f"##### Selectivity of {st.session_state.select_college}")
    st.markdown(f"* The Barron's selectivity index is ***{cur_wide['barrons']}***")
    st.markdown(f"* The tier of the college is classified as ***{cur_wide['tier_name']}***")
    sat_avg_str = "unavailable" if cur_wide['sat_avg_2013'] == 0 else f"{cur_wide['sat_avg_2013']:.0f} ( {st.session_state.selected_pct['sat_avg_2013']:.1f} percentile )"
    st.markdown(f"* The average SAT score (in 2013) is ***{sat_avg_str}***")
    st.markdown(f"* The acceptance rate (in 2013) is ***{100 - 100*cur_wide['scorecard_rej_rate_2013']:.1f}% ( {100-st.session_state.selected_pct['scorecard_rej_rate_2013']:.1f} percentile )***.")
    st.markdown(f"##### Financial Aspects of {st.session_state.select_college}")
    st.markdown(f"* The tuitions and fees (in 2013) is ***${cur_wide['sticker_price_2013']:,.0f} ( {st.session_state.selected_pct['sticker_price_2013']:.1f} percentile )***.")
    st.markdown(f"* The median parent household income is ***${cur_wide['par_median']:,.0f} ( {st.session_state.selected_pct['par_median']:.1f} percentile )***.")
    st.markdown(f"* About ***{cur_wide['par_top1pc']:,.1f}% ( {st.session_state.selected_pct['par_top1pc']:.1f} percentile )*** are from households with top 1% income.")
    grad_rate_str = "unavailable" if cur_wide['grad_rate_150_p_2013'] == 0 else f"{100*cur_wide['grad_rate_150_p_2013']:.1f}% ( {st.session_state.selected_pct['grad_rate_150_p_2013']:.1f} percentile )"
    st.markdown(f"* Graduation rate (within 6 years) is ***{grad_rate_str}***.")
    st.markdown(f"##### Demographic Distribution of {st.session_state.select_college}")
    st.markdown(f"* About ***{100*cur_wide['asian_or_pacific_share_fall_2000']:,.1f}% ( {st.session_state.selected_pct['asian_or_pacific_share_fall_2000']:.1f} percentile )*** of students are Asian or Pacific Islander (in 2000).")
    st.markdown(f"* About ***{100*cur_wide['black_share_fall_2000']:,.1f}% ( {st.session_state.selected_pct['black_share_fall_2000']:.1f} percentile )*** of students are Black (in 2000).")
    st.markdown(f"* About ***{100*cur_wide['hisp_share_fall_2000']:,.1f}% ( {st.session_state.selected_pct['hisp_share_fall_2000']:.1f} percentile )*** of students are Hispanic (in 2000).")
    st.markdown(f"* About ***{100*cur_wide['alien_share_fall_2000']:,.1f}% ( {st.session_state.selected_pct['alien_share_fall_2000']:.1f} percentile )*** of students are Non-resident alien (in 2000).")
    st.markdown(f"##### ~10 Years After Graduating {st.session_state.select_college}...")
    st.markdown(f"* Their median income is ***${cur_wide['k_median']:,.0f} ( {st.session_state.selected_pct['k_median']:.1f} percentile )***.")
    st.markdown(f"* About ***{100*cur_wide['k_married']:,.1f}% ( {st.session_state.selected_pct['k_married']:.1f} percentile )*** are married.")
    st.markdown(f"* About ***{cur_wide['mr_kq5_pq1']:,.1f}% ( {st.session_state.selected_pct['mr_kq5_pq1']:.1f} percentile )*** of students who have parents in the Bottom 20% of the income distribution and reach the Top 20% of the income distribution (called Mobility Rate).")

    st.markdown(f"### SAT Scores by year")
    chart_sat = alt.Chart(
            cur_tall[cur_tall.COLUMN.isin(['SATCM25','SATCM75','SATCMMID'])].replace(
                {'COLUMN': {'SATCM25':  '25th percentile of combined SAT score', 
                            'SATCMMID': 'Median combined SAT score', 
                            'SATCM75':  '75th percentile of combined SAT score'}
                }
            )
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title='SAT Score')),
        color = alt.Color('COLUMN', legend=alt.Legend(title='Types')),
    )
    st.altair_chart(alt.layer(chart_sat).interactive(), theme="streamlit", use_container_width=True)

    st.markdown(f"### ACT Scores by year")
    chart_sat = alt.Chart(
            cur_tall[cur_tall.COLUMN.isin(['ACTCM25','ACTCM75','ACTCMMID'])].replace(
                {'COLUMN': {'ACTCM25':  '25th percentile of combined ACT score', 
                            'ACTCMMID': 'Median combined ACT score', 
                            'ACTCM75':  '75th percentile of combined ACT score'}
                }
            )
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title='SAT Score')),
        color = alt.Color('COLUMN', legend=alt.Legend(title='Types')),
    )
    st.altair_chart(alt.layer(chart_sat).interactive(), theme="streamlit", use_container_width=True)

    st.markdown(f"### Tuitions and fees by year")
    chart_tuition = alt.Chart(
            cur_tall[cur_tall.COLUMN.isin(['TUITIONFEE_IN','TUITIONFEE_OUT','TUITFTE'])].replace(
                {'COLUMN': {'TUITIONFEE_IN': 'In-State Tuition', 
                           'TUITIONFEE_OUT': 'Out-of-State Tuition', 
                           'TUITFTE': 'Average Tuition Revenue per Student'}
                }
            )
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title='USD')),
        color = alt.Color('COLUMN', legend=alt.Legend(title='Types')),
    )

    st.altair_chart(alt.layer(chart_tuition).interactive(), theme="streamlit", use_container_width=True)

    st.markdown(f"### Demographic distribution by year")
    df_demo = cur_tall[cur_tall.COLUMN.isin(['UGDS_WHITE','UGDS_BLACK','UGDS_HISP','UGDS_ASIAN','UGDS_AIAN','UGDS_NHPI','UGDS_2MOR','UGDS_NRA','UGDS_UNKN'])].replace(
                {'COLUMN': {'UGDS_WHITE':'White',
                            'UGDS_BLACK':'Black',
                            'UGDS_HISP':'Hispanic',
                            'UGDS_ASIAN':'Asian',
                            'UGDS_AIAN':'American Indian/Alaska Native',
                            'UGDS_NHPI':'Native Hawaiian/Pacific Islander',
                            'UGDS_2MOR':'Two or more races',
                            'UGDS_NRA':'Non-resident aliens',
                            'UGDS_UNKN':'Unknown'}
                }
            )
    df_demo = df_demo[df_demo.YEAR > 2010]
    chart_demo = alt.Chart(
            df_demo
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title='Fraction')),
        color = alt.Color('COLUMN', legend=alt.Legend(title='Race')),
    )
    st.altair_chart(alt.layer(chart_demo).interactive(), theme="streamlit", use_container_width=True)

    st.markdown(f"### Median income by year")
    df_earning = cur_tall[cur_tall.COLUMN.isin(['MD_EARN_WNE_P10','MD_EARN_WNE_P8','MD_EARN_WNE_P6'])].replace(
                {'COLUMN': {'MD_EARN_WNE_P10':'10 years after entry',
                            'MD_EARN_WNE_P8':'8 years after entry',
                            'MD_EARN_WNE_P6':'6 years after entry'}
                }
            )
    #df_earning = df_demo[df_demo.YEAR > 2010]
    chart_earning = alt.Chart(
            df_earning
        ).mark_line(point=True).encode(
        x = alt.X('YEAR', axis=alt.Axis(format='d')),
        y = alt.Y('VALUE', axis=alt.Axis(title='USD')),
        color = alt.Color('COLUMN', legend=alt.Legend(title='Median Income')),
    )
    st.altair_chart(alt.layer(chart_earning).interactive(), theme="streamlit", use_container_width=True)

#    st.dataframe(cur_tall[cur_tall.COLUMN.isin(['TUITIONFEE_IN','TUITIONFEE_OUT','TUITFTE'])])

