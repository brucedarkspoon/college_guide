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

## load the data just once across the app
cgs.load_data()

## change the session variables when the college is selected
def update_college():
    idx = st.session_state.df_wide[st.session_state.df_wide['name'] == st.session_state.select_college].index[0]
    st.session_state.selected_wide = st.session_state.df_wide.iloc[idx]
    st.session_state.selected_pct = st.session_state.df_wide_pct.iloc[idx]
    st.session_state.selected_id = st.session_state.selected_wide['id']
    st.session_state.selected_tall = st.session_state.df_tall[st.session_state.df_tall['INSTID'] == st.session_state.selected_id]

# Title of the application
st.title(f"{cgs.app_name} - View")

# Input to search for a University

col1, col2 = st.columns([1, 1])
with col1:
    col1.markdown("#### Select or enter college name.")
with col2:
    expander = col2.expander("See explanation")
    expander.markdown("* Enter a college name in the dropdown menu below.")
    expander.markdown("* Or select a college from the dropdown menu.")
    expander.markdown("* Once a college is selected, the information will be displayed below.")

select_college = st.selectbox('Select/Enter a University Name', st.session_state.df_wide['name'].unique(), key = 'select_college', on_change = update_college)

def get_metric_str(df, name, frac2percent=False):
#    print(df[name],type(df[name]))
    if np.isnan(df[name]):
        return "unavailable"
    elif frac2percent:
        return f"{100*df[name]:,.1f}% ( {st.session_state.selected_pct[name]:.1f} percentile )"
    else:
        return f"{df[name]:,.0f} ( {st.session_state.selected_pct[name]:.1f} percentile )"

if 'selected_wide' in st.session_state:
    cur_wide = st.session_state.selected_wide
    cur_tall = st.session_state.selected_tall

    st.markdown(f"#### You selected : {st.session_state.select_college}")
    ex_key = st.expander(f"Hide/Show Key Information of {st.session_state.select_college}", expanded=True)
    col1, col2 = ex_key.columns([1, 1])
    with col1:
        col1.markdown(f"##### Basic Information")
        col1.markdown(f"* ***{cur_wide['tier_name']}*** college")
        col1.markdown(f"* Located in ***{cur_wide['school__city']}, {cur_wide['school__state']}***")
        col1.markdown(f"* Offers a ***{cur_wide['iclevel']}*** program.")
        col1.markdown(f"* The number of enrolled student is ***{get_metric_str(cur_wide, 'student__size')}***")
        col1.markdown("")
        col1.markdown(f"##### Selectivity")
        col1.markdown(f"* Classified as '***{cur_wide['barrons']}***' by the Barron's Selectivity index")
        col1.markdown(f"* Average SAT-equivalent score is ***{get_metric_str(cur_wide,'admissions__sat_scores__average__overall')}***.")
        col1.markdown(f"* Median ACT score is ***{get_metric_str(cur_wide,'admissions__act_scores__midpoint__cumulative')}***.")
        col1.markdown(f"* Admission rate is ***{get_metric_str(cur_wide,'admissions__admission_rate__overall',frac2percent=True)}***.")
        col1.markdown("")
        col1.markdown(f"##### Financial Aspects")
        col1.markdown(f"* In-state tution & fee is ***${get_metric_str(cur_wide,'cost__tuition__in_state')}***.")
        col1.markdown(f"* Out-of-state tution & fee is ***${get_metric_str(cur_wide,'cost__tuition__out_of_state')}***.")
        col1.markdown(f"* Net tuition revenue per student is ***${get_metric_str(cur_wide,'school__tuition_revenue_per_fte')}***.")
        col1.markdown(f"* Instructional expenditure per student is ***${get_metric_str(cur_wide,'school__instructional_expenditure_per_fte')}***.")
        col1.markdown(f"* About ***{get_metric_str(cur_wide,'aid__pell_grant_rate',frac2percent=True)}*** of students receive Pell Grant.")  
        col1.markdown(f"* The median parent household income is ***${get_metric_str(cur_wide,'par_median')}***.")
        col1.markdown(f"* About ***{cur_wide['par_top1pc']:,.1f}% ( {st.session_state.selected_pct['par_top1pc']:.1f} percentile )*** are from households with top 1% income.")
    with col2:
        col2.markdown(f"##### Demographic Distribution")
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'student__demographics__race_ethnicity__white',frac2percent=True)}*** are White.")  
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'student__demographics__race_ethnicity__black',frac2percent=True)}*** are Black.")  
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'student__demographics__race_ethnicity__hispanic',frac2percent=True)}*** are Hispanics.")  
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'student__demographics__race_ethnicity__asian',frac2percent=True)}*** are Asians.")  
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'student__demographics__race_ethnicity__non_resident_alien',frac2percent=True)}*** are international students.") 
        col2.markdown(f"* About ***{get_metric_str(cur_wide,'female',frac2percent=True)}*** are females.")  
        col2.markdown("")
        col2.markdown(f"##### Expected Outcome")
        col2.markdown(f"* Graduation rate (within 6 years) is ***{get_metric_str(cur_wide,'completion__rate_suppressed__four_year',frac2percent=True)}***.")
        col2.markdown(f"* Median income after 10 years of entry is ***${get_metric_str(cur_wide,'earnings__10_yrs_after_entry__median')}***.")
        col2.markdown(f"* Mobility rate is ***{cur_wide['mr_kq5_pq1']:,.1f}% ( {st.session_state.selected_pct['mr_kq5_pq1']:.1f} percentile )*** (i.e. student reach top 20% income given parents had bottom 20% income).")

    chart_groups = {
        "SAT Scores": ['SATCM25','SATCM75','SATCMMID'],
        "ACT Scores": ['ACTCM25','ACTCM75','ACTCMMID'],
        "Tuition and Fees": ['TUITIONFEE_IN','TUITIONFEE_OUT','TUITFTE'],
        "Degree Distribution": ['PCIP01','PCIP04','PCIP11','PCIP13','PCIP14','PCIP26','PCIP27','PCIP45','PCIP50','PCIP51','PCIP52'],
        "Demographic Distribution": ['UGDS_WHITE','UGDS_BLACK','UGDS_HISP','UGDS_ASIAN','UGDS_AIAN','UGDS_NHPI','UGDS_2MOR','UGDS_NRA','UGDS_UNKN'],
        "Median Income": ['MD_EARN_WNE_P10','MD_EARN_WNE_P8','MD_EARN_WNE_P6'],
    }

    ex_chart = st.expander(f"Hide/Show Charts of {st.session_state.select_college}", expanded=True)
    for key in chart_groups.keys():
        colnames = chart_groups[key]
        chart = alt.Chart(
                cur_tall[cur_tall.COLUMN.isin(colnames)].replace(
                    {'COLUMN' : {x:cgs.lts[x] for x in colnames} }
                )
            ).mark_line(point=True).encode(
            x = alt.X('YEAR', axis=alt.Axis(format='d')),
            y = alt.Y('VALUE', axis=alt.Axis(title=key)),
            color = alt.Color('COLUMN', legend=alt.Legend(title='Types',labelLimit=500)),
        )
        ex_chart.altair_chart(alt.layer(chart).interactive(), theme="streamlit", use_container_width=True)