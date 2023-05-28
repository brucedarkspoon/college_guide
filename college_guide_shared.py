import streamlit as st
import pandas as pd
import numpy as np
import yaml
import os, sys, math

## This code contains shared functions and variables in the college_guide app
## Usage: import college_guide_shared as cgs

app_name = "College Selection Guide"

## Defines the color maps for classifying each college
color_maps = {
    'barrons': {
        '1 - Elite':            [255, 100, 100, 140],
        '2 - Highly Selective': [100, 100, 255, 140],
        '3 - Selective':        [100, 255, 100, 140],
        '4 - Selective':        [100, 255, 100, 140],
        '5 - Selective':        [100, 255, 100, 140],
        '9 - Special':          [255, 100, 255, 140],
        '999 - Non-selective':  [255, 255, 100, 140],
    },
    'iclevel': {
        '1-year':[100, 255, 100, 140], 
        '2-year':[255, 100, 100, 140],
        '4-year':[100, 100, 255, 140],
    },
    'public': {
        'public':[100, 100, 255, 140], 
        'private':[255, 100, 100, 140]
    },
    'region': {
        'Midwest':[100, 100, 255, 140],
        'Northeast':[255, 100, 100, 140],
        'South':[100, 255, 100, 140],
        'West':[255, 255, 100, 140],
    },
}
color_map_desc = {
    'barrons': "Color by Barron's Selectivity Index",
    'iclevel': "Color by Degree Type",
    'public': "Color by Public/Private",
    'region': "Color by Region",
}

## column names and their descriptions for the tall data
lts = {
    'SAT_AVG' : 'Average SAT equivalent score of students admitted', 
    'SATCM25' : '25th percentile of cumulative SAT scores', 
    'SATCM75' : '75th percentile of cumulative SAT scores', 
    'SATCMMID': 'Median of cumulative SAT scores', 
    'ACTCM25' : '25th percentile of cumulative ACT scores', 
    'ACTCM75' : '75th percentile of cumulative ACT scores', 
    'ACTCMMID': 'Median of cumulative ACT scores',
    'ADM_RATE' : "Admission rate",
    'TUITIONFEE_IN' : "In-state tuition and fees", 
    'TUITIONFEE_OUT' : "Out-of-state tuition and fees", 
    'TUITFTE' : "Average tuition revenue per student", 
    'INEXPFTE' : "Average instructional expenditure per student",
    'UGDS': 'Student size',
    'UGDS_WHITE' : "Percent of white students", 
    'UGDS_BLACK' : "Percent of black students", 
    'UGDS_HISP' : "Percent of Hispanic students", 
    'UGDS_ASIAN' : "Percent of Asian students", 
    'UGDS_AIAN' : "Percent of American Indian/Alaska Native students", 
    'UGDS_NHPI' : "Percent of Native Hawaiian/Pacific Islander students", 
    'UGDS_2MOR' : "Percent of students who are two or more races", 
    'UGDS_NRA' : "Percent of international students", 
    'UGDS_UNKN' : "Percent of students whose race is unknown", 
    'MD_EARN_WNE_P10' : "Median earnings of students after 10 years of entry", 
    'MD_EARN_WNE_P8'  : "Median earnings of students after 8 years of entry",
    'MD_EARN_WNE_P6'  : "Median earnings of students after 6 years of entry",
    'C150_4' : "Graduation rate within 6 years (150%)",
    'PCTPELL' : "Share of students receiving Pell grants",
    'LOAN_EVER' : "Share of students who ever received a federal student loan",
    'PCIP01' : 'Share of Agriculture Degree Students',
    'PCIP04' : 'Share of Architecture Degree Students',
    'PCIP11' : 'Share of Computer & Information Science Degree Students',
    'PCIP13' : 'Share of Education Degree Students',
    'PCIP14' : 'Share of Engineering Degree Students',
    'PCIP15' : 'Share of Engineering Technology and Related Degree Students',
    'PCIP16' : 'Share of Foreign Language, Literature, Linguistics Degree Students',
    'PCIP22' : 'Share of Legal Profession Degree Students',   
    'PCIP24' : 'Share of Liberal Arts And Sciences, General Studies And Humanities Degree Students',   
    'PCIP26' : 'Share of Biological and Biomedical Science Degree Students',
    'PCIP27' : 'Share of Mathematics and Statistics Degree Students',
    'PCIP29' : 'Share of Military Technologies And Applied Sciences Degree Students',
    'PCIP30' : 'Share of Multi/Interdisciplinary Degree Students',
    'PCIP38' : 'Share of Philosophy and Religious Studies Degree Students',
    'PCIP40' : 'Share of Physical Science Degree Students',
    'PCIP42' : 'Share of Psychology Degree Students',
    'PCIP45' : 'Share of Social Science Degree Students',
    'PCIP50' : 'Share of Visual And Performing Arts Degree Students',
    'PCIP51' : 'Share of Health Degree Students',
    'PCIP52' : 'Share of Business Degree Students',
    'PCIP54' : 'Share of History Degree Students',
}

## column names and their descriptions for the quantitative trait wide data
qts = { 'par_median' : 'Median Income of Parents at Admission (adjusted)',
        'k_median' : 'Median Income of Child ~10 years After Graduation (adjusted)',
        'par_q1' : 'Fraction of Parents with Bottom 20% Income',
        'par_top1pc' : 'Fraction of Parents with Top 1% Income',
        'mr_kq5_pq1' : 'Mobility Rate 20% (Parent Bottom 20% -> Child Top 20% Income)',
        'mr_ktop1_pq1' : 'Mobility Rate 1% (Parent Bottom 20% -> Child Top 1% Income)',
        'count' : 'Cohort Size',
        'sat_avg_2013' : 'SAT Average Score in 2013',
        'sticker_price_2013' : 'Annual Tuition + Fees in 2013',
        'grad_rate_150_p_2013' : 'Graduation Rate in 150% Time in 2013',
        'scorecard_netprice_2013' : 'Total Tuition + Fees for Bottom 20% Income in 2013',
        'scorecard_rej_rate_2013' : 'Fraction of Applicants Rejected in 2013',
        'trend_parq1' : 'Change in % of Parents in Bottom 20% Income',
        'trend_bottom40' : 'Change in % of Parents in Bottom 40% Income',
        'female' : 'Percent of Female Students',
        'k_married' : 'Percent of Students Married at age ~33',
        'student__size' : 'Undergrad Enrollment',
        'admissions__sat_scores__average__overall' : 'SAT Average Score',
        'admissions__admission_rate__overall' : 'Acceptance Rate',
        'admissions__act_scores__midpoint__cumulative' : 'ACT Median Score',
        'cost__tuition__in_state' : 'In-State Tuition',
        'cost__tuition__out_of_state' : 'Out-of-State Tuition',
        'school__tuition_revenue_per_fte' : 'Tuition Revenue per Student',
        'student__demographics__race_ethnicity__white' : 'Percent of White Students',
        'student__demographics__race_ethnicity__black' : 'Percent of Black Students',
        'student__demographics__race_ethnicity__hispanic' : 'Percent of Hispanic Students',
        'student__demographics__race_ethnicity__asian' : 'Percent of Asian Students',
        'student__demographics__race_ethnicity__non_resident_alien' : 'Percent of International Students',
        'earnings__10_yrs_after_entry__median' : 'Median Earnings 10 years after Entry',
        'aid__pell_grant_rate' : 'Percent of Pell Grant Recipients',   
        'student__demographics__median_family_income' : 'Median Family Income',
        'school__instructional_expenditure_per_fte' : 'Instructional Expenditure per Student',
        'completion__rate_suppressed__four_year' : 'Graduation Rate in 6 years',
        }
## categorical variables used for grouping in the chart
cats = {
    'tier_name' : 'College Tier',
    'type' : 'College Type',
    'public' : 'Public University',
    'barrons' : "Barron's Selectivity Index",
    'region' : 'Region',
    'czname' : 'Commuting Zone',
    'state' : 'State',
    'iclevel' : 'Degree Type',
}
## other key variables to be included
oths = {
    'id': 'Institution ID',
    'name': 'Name of the school',
    'school__city': 'City of the school',
    'school__state': 'State of the school',
    'lon': 'Longitude',
    'lat': 'Latitude',
}

# Load all data together
@st.cache_data
def load_data():
    #if 'df_wide' not in st.session_state:
    widef = "College_Scorecard_Mobility_Latest_NonEmpty.20230524.tsv"
    tallf = "MERGED_1996_2022_ALL_NONEMPTY_TALL.SELECTED_SATCM.tsv.gz"

    ## load wide-formatted data
    df_wide = pd.read_csv(widef, sep="\t")
    ## rename columns in the wide-formatted data
    df_wide = df_wide.rename({"location.lat": "lat", "location.lon": "lon"}, axis=1)
    ## rename columns to avoid problems with altair
    df_wide.columns = [x.replace(".", "__") for x in df_wide.columns]
    ## subset columns of interest
    colnames = list(oths.keys()) + list(cats.keys()) + list(qts.keys())

    df_wide = df_wide[colnames]
    ## remove specific colleges that have misleading data
    ids_to_remove = [183026] ## currently only Southeran New Hampshire University
    df_wide = df_wide[~df_wide['id'].isin(ids_to_remove)]

    ## calculate percentiles
    df_wide_pct = df_wide.rank(pct=True) * 100
    #st.session_state['df_wide_pct'] = df_wide_pct

    ## add color key
    color_key = 'public'
    df_wide['col'] = [color_maps[color_key][x] for x in df_wide[color_key]]
    df_wide['radius'] = np.sqrt(df_wide['student__size']) * 125

    #st.session_state['df_wide'] = df_wide

    ## load tall-formatted data
    df_tall = pd.read_csv(tallf, sep="\t", compression='gzip')
    df_tall = df_tall[~((df_tall['COLUMN'].str.startswith('UGDS_')) & (df_tall['YEAR'] < 2011)) | df_tall['INSTID'].isin(ids_to_remove)]
    st.session_state['df_tall'] = df_tall
    return df_wide, df_wide_pct, df_tall
