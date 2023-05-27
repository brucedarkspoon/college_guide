import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import yaml
import os, sys, math
import college_guide_shared as cgs
pd.options.mode.chained_assignment = None

st.set_page_config(layout="wide") # Set the page layout to wide

st.subheader(f"Welcome to the {cgs.app_name}!")
st.markdown(f"#### What is the ***{cgs.app_name}***?")
st.write(f"The ***{cgs.app_name}*** is a tool for prospective college students in the United States.")
st.write("It allows users to search for colleges based on various criteria and provide in-depth information with visualization.")
st.write("Specifically, it allows you to:")
st.markdown("* ***Filter*** and visualize colleges based on the selected criteria (e.g. SAT scores, tuition, expected income))")
st.markdown("* ***View*** detailed information on the specific college you are interested in")
st.markdown("* ***Compare*** between selected colleges based on selected metrics")
st.markdown(f"#### Overview of the Data used in the ***{cgs.app_name}***")
st.markdown(f"* The ***{cgs.app_name}*** uses the data from [College Scorecard](https://collegescorecard.ed.gov/data/) and [Opportunity Insights](https://opportunityinsights.org/data/)")
st.markdown(f"* The data from College Scorecard is used to provide basic information on colleges and their students.")
st.markdown("* This data track the information of students who enrolled in college in ***1996-2022***.")
st.markdown("* Whenever possible, latest data is used to provide the most up-to-date information.")
st.markdown("* When displaying longitudinal data, data across all available years of admission to college were used.")
st.markdown(f"* The data from Opportunity Insights is used to provide information on the income of parents.")
