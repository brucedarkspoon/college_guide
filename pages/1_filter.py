import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import yaml
import os, sys, math

## avoid warning message
pd.options.mode.chained_assignment = None

## Set the default page layout to wide
st.set_page_config(layout="wide") 

if 'app_name' not in st.session_state:
    st.session_state['app_name'] = "College Selection Guide"

## define CheckBoxGroup class to create multiple checkboxes
class CheckBoxGroup:
    def __init__(self, name, values, update_func, num_cols=1, component = st):
        self.name = name        ## variable name in the pandas dataframe
        self.values = values    ## unique values in the pandas dataframe
        self.prefix = "chk_" + name  ## prefix for the session_state variable    
        self.update_func = update_func ## function to call when the checkbox is updated
        cols = component.columns(num_cols)
        self.chk = []
        num_rows = (len(values) + num_cols - 1) // num_cols
        for i in range (len(values)):
            with cols[i // num_rows]:
                self.chk.append(st.checkbox(values[i],
                    value=True, on_change = update_func, key = self.prefix + '_' + str(i)))
#        self.chk = [st.checkbox(values[i], value=True, on_change = update_func, key = self.prefix + '_' + str(i)) for i in range(len(values))]
        st.session_state.chk_dict[self.name] = self

    ## this function is called inside the update_filter() function to get the selected items
    def get_selected_list(self):
        # scan chk_tier_0, ... chk_tier_N to see which values are selected
        chk_selected = []
        for i in range(len(self.values)):
            if st.session_state[self.prefix + '_' + str(i)]:
                chk_selected.append(self.values[i])
        return chk_selected

    ## function to reset everything to default (all checkboxes are selected)
    def reset(self):
        for i in range(len(self.values)):
            st.session_state['chk_' + self.name + '_' + str(i)] = True

## define color maps for possible values of the categorical variables in the map
color_maps = {
    'barrons': {
        '1 - Elite':            [127, 201, 127, 140],
        '2 - Highly Selective': [190, 174, 212, 140],
        '3 - Selective':        [253, 192, 134, 140],
        '4 - Selective':        [253, 192, 134, 140],
        '5 - Selective':        [253, 192, 134, 140],
        '9 - Special':          [255, 255, 153, 140],
        '999 - Non-selective':  [56, 108, 176, 140],
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
}

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
        }

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

oths = {
    'name': 'Name of the school',
    'school__city': 'City of the school',
    'school__state': 'State of the school',
    'lon': 'Longitude',
    'lat': 'Latitude',
}


# Loading the data
@st.cache_data
def load_data():    
    ## Load the wide-formatted data
    tsvf = "College_Scorecard_Mobility_Latest_NonEmpty.20230524.tsv"
    df = pd.read_csv(tsvf, sep="\t")
    df = df.rename({"location.lat": "lat", "location.lon": "lon"}, axis=1)

    df.columns = [x.replace(".", "__") for x in df.columns]

    colnames = list(oths.keys()) + list(cats.keys()) + list(qts.keys())
    df = df[colnames]
    color_key = 'public'
    df['col'] = [color_maps[color_key][x] for x in df[color_key]]
    df['radius'] = np.sqrt(df['student__size']) * 125

    yamlf = "data.yaml"
    with open(yamlf, 'r') as file:
        yaml_data = yaml.safe_load(file)
    col_dict = yaml_data['dictionary'] 
    return df, col_dict

def update_filter():
    # scan chk_tier_0, ... chk_tier_N to see which values are selected
    name2selected = {}
    for name in st.session_state.chk_dict:
        chk_box_grp = st.session_state.chk_dict[name]
        chk_selected = chk_box_grp.get_selected_list()
        name2selected[name] = chk_selected

    ## filter by checkboxes and multiselects first
    df_filt =  df[ (df['region'].isin(name2selected['region'])) &
#                   (df['tier_name'].isin(name2selected['tier_name'])) &
                    (df['type'].isin(name2selected['type'])) &
                    (df['barrons'].isin(name2selected['barrons'])) &
                    (df['state'].isin(st.session_state.multi_states))]

    ## filter by sliders    
    for key in slider_dict:
        colname, minval, maxval = slider_dict[key]
        if st.session_state[key][0] > minval or st.session_state[key][1] < maxval:
            if minval == 0 and maxval == 100:
                df_filt = df_filt[
                            (df_filt[colname] >= st.session_state[key][0]/100) &
                            (df_filt[colname] <= st.session_state[key][1]/100)
                            ]
            else:
                df_filt = df_filt[
                            (df_filt[colname] >= st.session_state[key][0]) &
                            (df_filt[colname] <= st.session_state[key][1])
                            ]


    st.session_state.df_filt = df_filt

def update_reset():
    #multi_states = state_unique_values
    for key in slider_dict:
        colname, minval, maxval = slider_dict[key]
        st.session_state[key] = [minval, maxval]
    for name in st.session_state.chk_dict:
        chk_box_grp = st.session_state.chk_dict[name]
        chk_box_grp.reset()
    update_filter()

def update_map_color_key():
    color_key = st.session_state.map_color_key
    st.session_state.df_filt['col'] = [color_maps[color_key][x] for x in st.session_state.df_filt[color_key]]
    #update_filter()

## create a dictionary that contains name, min, max values for each metric for slider
slider_dict = {
    'a0_slider_sat_avg': ['admissions__sat_scores__average__overall', 400, 1600],
    'a1_slider_act_mid': ['admissions__act_scores__midpoint__cumulative', 1, 36],
    'a2_slider_admit_rate': ['admissions__admission_rate__overall', 0, 100],
    'b0_slider_white': ['student__demographics__race_ethnicity__white', 0, 100],
    'b1_slider_black': ['student__demographics__race_ethnicity__black', 0, 100],
    'b2_slider_hispanic': ['student__demographics__race_ethnicity__hispanic', 0, 100],
    'b3_slider_asian': ['student__demographics__race_ethnicity__asian', 0, 100],
    'b4_slider_nra': ['student__demographics__race_ethnicity__non_resident_alien', 0, 100],

    'c0_slider_tuition_in_state' : ['cost__tuition__in_state', 0, 100000],
    'c1_slider_tuition_out_of_state' : ['cost__tuition__out_of_state', 0, 100000],
    'c2_slider_pell_grant_state' : ['aid__pell_grant_rate', 0, 100],
    'd0_slider_earning_10yrs' : ['earnings__10_yrs_after_entry__median', 0, 200000],
    'd1_slider_par_median' : ['par_median', 0, 200000],
    'e0_slider_female' : ['female', 0, 100],
    'e1_slider_k_married' : ['k_married', 0, 100],
    'e2_student_size' : ['student__size', 0, 20000],
} 

df, col_dict = load_data()

tier_name_unique_values = sorted(list(df['tier_name'].unique()))
selectivity_unique_values = sorted(list(df['barrons'].unique()))
type_unique_values = sorted(list(df['type'].unique()))
state_unique_values = sorted(list(df['state'].unique()))
region_unique_values = sorted(list(df['region'].unique()))

## Initialize session variables
## create an initially filtered data and store in the session.
if 'df_filt' not in st.session_state:
    st.session_state['df_filt'] = df #[['id', 'school.name', 'lon', 'lat', 'barrons', 'public', 'student.size']]
    df_session = st.session_state['df_filt']
else:
    df_session = st.session_state['df_filt']

if 'chk_dict' not in st.session_state:
    st.session_state.chk_dict = {}

# Title of the application
st.title(f"{st.session_state.app_name} - Filter")

# Input to search for a University
# st.markdown("#### Select or search for a college in the dropdown menu.")
# select_college = st.selectbox('Select/Enter a University Name', st.session_state.df_filt['school.name'].unique(), key = 'select_college', on_change = update_college)

col1, col2 = st.columns([1, 1])
with col1:
    col1.markdown(f"#### Currently, {st.session_state.df_filt.shape[0]} colleges are selected.")
with col2:
    expander = col2.expander("See explanation")
    expander.markdown("* Selected colleges are shown in the map below.")
    expander.markdown("* Hover over each circle to see detailed info of each college.")
    expander.markdown("* Use the dropdown menu on the right to change the colors")
    expander.markdown("* Filtering criteria can be selected below the map")

#st.markdown("*Selected colleges are shown in the map. Hover over to see detailed info. Use the dropdown menu to change the colors.*")

expander_map = st.expander(f"Hide/show the map of {st.session_state.df_filt.shape[0]} colleges", expanded=True)
r = pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=37.76,
        longitude=-100.4,
        zoom=3.5,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data = df_session.fillna(""),
            get_position='[lon, lat]',
            get_fill_color='col',
            get_line_color='[0, 0, 0]',
            get_radius='radius',
            line_width_min_pixels=100,
            pickable=True,
        ),
    ],
    tooltip={
        'html': '<b>Name:</b> {name} ({school__city}, {school__state})<br/><b>Barrons Selectivity:</b> {barrons}<br/><b>Type:</b> {public}, {iclevel} <br/><b>Student Size:</b> {student__size}<br/><b>SAT / ACT:</b> {admissions__sat_scores__average__overall} / {admissions__act_scores__midpoint__cumulative}<br/><b>Acceptance Rate:</b> {admissions__admission_rate__overall}<br/><b>In/Out-State Tuitions: </b> ${cost__tuition__in_state} / ${cost__tuition__out_of_state}',
        'style': {
            'color': 'white'
        }
    }
)
col1, col2 = expander_map.columns([3, 1])
with col2:
    col2.selectbox('Colors', sorted(color_maps), 
                 key = 'map_color_key', on_change = update_map_color_key, 
                 label_visibility='collapsed', index=2)
expander_map.pydeck_chart(r)

# sat_scores_slider, sat_scores_chk = make_slider(df, 'Select SAT Scores Range', 'admissions.sat_scores.average.overall')
# Input to select cost to attend
# cost_to_attend_slider, cost_to_attend_chk = make_slider(df, 'Select Cost to Attend Range', 'cost.avg_net_price.overall')
sliders = {}

expander_filt = st.expander(f"Hide/show criteria for filtering {st.session_state.df_filt.shape[0]} colleges", expanded=True)
expander_filt.button('Reset All', key = 'reset_all', on_click = update_reset)
col1, col2, col3 = expander_filt.columns([1, 1, 3])
with col1:
    col1.markdown("**Region**")
    chk_region = CheckBoxGroup('region', region_unique_values, update_filter, 1, col1)
with col2:
    col2.markdown("**College Type**")
    chk_type = CheckBoxGroup('type', type_unique_values, update_filter, 1, col2)
with col3:
    col3.markdown("**Barron's Selectivity Index**")
    chk_selectivity = CheckBoxGroup('barrons', selectivity_unique_values, update_filter, 3, col3)

col1, col2, col3 = expander_filt.columns([2, 2, 2],gap="small")
slider_keys = sorted(slider_dict)
with col1:
    multi_states = col1.multiselect("**States**", state_unique_values, default=state_unique_values, key = "multi_states", on_change = update_filter)
with col2:
    for i in range((len(slider_keys)+1)//2):
        col2.slider(qts[slider_dict[slider_keys[i]][0]], 
                    min_value=slider_dict[slider_keys[i]][1], 
                    max_value=slider_dict[slider_keys[i]][2], 
                    value=(slider_dict[slider_keys[i]][1], slider_dict[slider_keys[i]][2]), 
                    key = slider_keys[i], on_change = update_filter)
with col3:
    for i in range((len(slider_keys)+1)//2,len(slider_keys)):
        col3.slider(qts[slider_dict[slider_keys[i]][0]], 
                    min_value=slider_dict[slider_keys[i]][1], 
                    max_value=slider_dict[slider_keys[i]][2], 
                    value=(slider_dict[slider_keys[i]][1], slider_dict[slider_keys[i]][2]), 
                    key = slider_keys[i], on_change = update_filter)

def foo(widget_instance, payload):
    print(f"{widget_instance} clicked with payload {payload}")

expander_chart = st.expander(f"Hide/show chart", expanded=True)
col1, col2, col3 = expander_chart.columns(3)
with col1:
    xaxis = col1.selectbox("X-axis", qts.keys(), format_func=lambda x: qts[x], index=0)
with col2:
    yaxis = col2.selectbox("Y-axis", qts.keys(), format_func=lambda x: qts[x], index=1)
with col3:
    group = col3.selectbox("Group", cats.keys(), format_func=lambda x: cats[x], index=3)
chart = alt.Chart(df).mark_circle().encode(
    x = alt.X(xaxis, axis=alt.Axis(title=qts[xaxis])),
    y = alt.Y(yaxis, axis=alt.Axis(title=qts[yaxis])),
    opacity = alt.value(0.1),
    color = alt.value("gray"),
    tooltip=[alt.Tooltip('name', title='College Name')])
df_filt_rename = st.session_state.df_filt
#df_filt_rename.columns = [x.replace(".", "_") for x in st.session_state.df_filt.columns]
chart_change = alt.Chart(df_filt_rename).mark_point().encode(
    x = alt.X(xaxis, axis=alt.Axis(title=qts[xaxis])),
    y = alt.Y(yaxis, axis=alt.Axis(title=qts[yaxis])),
    color = alt.Color(group, legend=alt.Legend(title=cats[group])),
    tooltip = [alt.Tooltip('name', title='College Name'),
                alt.Tooltip('admissions__sat_scores__average__overall', title='Average SAT'),
                alt.Tooltip('tier_name', title='College Tier'),
                alt.Tooltip('admissions__admission_rate__overall', title='Acceptance Rate'),
                alt.Tooltip('school__tuition_revenue_per_fte', title='Tuition Revenue per Student'),
                alt.Tooltip('earnings__10_yrs_after_entry__median', title='Median Earnings 10 years after Entry')
              ]
)

expander_chart.altair_chart(alt.layer(chart,chart_change).interactive(), theme="streamlit", use_container_width=True)

# Display the table of universities
expander_table = st.expander(f"Hide/show table", expanded=True)
expander_table.markdown("### Full List of Selected Colleges")
expander_table.dataframe(st.session_state.df_filt)