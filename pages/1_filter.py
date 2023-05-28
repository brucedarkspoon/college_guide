import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import altair as alt
import yaml
import os, sys, math
import college_guide_shared as cgs

## avoid warning message
pd.options.mode.chained_assignment = None

## Set the default page layout to wide
st.set_page_config(layout="wide") 

## load data (just once)
cgs.load_data()

## define CheckBoxGroup class to create multiple checkboxes
class CheckBoxGroup:
    def __init__(self, name, update_func, num_cols=1, component = st):
        self.name = name        ## variable name in the pandas dataframe
        self.values = st.session_state.uniq_vals[name] ## unique values in the pandas dataframe
        self.prefix = "chk_" + name  ## prefix for the session_state variable    
        self.update_func = update_func ## function to call when the checkbox is updated
        cols = component.columns(num_cols)
        self.chk = []
        num_rows = (len(self.values) + num_cols - 1) // num_cols
        for i in range (len(self.values)):
            with cols[i // num_rows]:
                self.chk.append(st.checkbox(self.values[i],
                    value=True, on_change = update_func, key = self.prefix + '_' + str(i)))
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
            st.session_state[self.prefix + '_' + str(i)] = True

def update_filter():
    # scan chk_tier_0, ... chk_tier_N to see which values are selected
    name2selected = {}
    for name in st.session_state.chk_dict:
        chk_box_grp = st.session_state.chk_dict[name]
        chk_selected = chk_box_grp.get_selected_list()
        name2selected[name] = chk_selected

    df = st.session_state.df_wide
    ## filter by checkboxes and multiselects first
    df_filt =  df[ (df['region'].isin(name2selected['region'])) &
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

def update_map_color_desc():
    for key in cgs.color_map_desc:
        if cgs.color_map_desc[key] == st.session_state.map_color_desc:
            color_key = key #st.session_state.map_color_desc
    st.session_state.df_filt['col'] = [cgs.color_maps[color_key][x] for x in st.session_state.df_filt[color_key]]

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

if 'uniq_vals' not in st.session_state:
    uniq_vals = {}
    uniq_vals_keys = ['tier_name', 'barrons', 'type', 'state', 'region']
    for key in uniq_vals_keys:
        uniq_vals[key] = sorted(list(st.session_state.df_wide[key].unique()))
    st.session_state['uniq_vals'] = uniq_vals

## Initialize session variables
## create an initially filtered data and store in the session.
if 'df_filt' not in st.session_state:
    st.session_state['df_filt'] = st.session_state.df_wide

if 'chk_dict' not in st.session_state:
    st.session_state.chk_dict = {}

# Title of the application
st.title(f"{cgs.app_name} - Filter")

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
def foo():
    print("foo")

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
            data = st.session_state.df_filt.fillna(""),
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
    },
)
col1, col2 = expander_map.columns([2, 1])
with col2:
    col2.selectbox('Colors', [cgs.color_map_desc[x] for x in sorted(cgs.color_maps)], 
                 key = 'map_color_desc', on_change = update_map_color_desc, 
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
    chk_region = CheckBoxGroup('region', update_filter, 1, col1)
with col2:
    col2.markdown("**College Type**")
    chk_type = CheckBoxGroup('type', update_filter, 1, col2)
with col3:
    col3.markdown("**Barron's Selectivity Index**")
    chk_selectivity = CheckBoxGroup('barrons', update_filter, 3, col3)

col1, col2, col3 = expander_filt.columns([2, 2, 2],gap="small")
slider_keys = sorted(slider_dict)
with col1:
    multi_states = col1.multiselect("**States**", st.session_state.uniq_vals['state'], default=st.session_state.uniq_vals['state'], key = "multi_states", on_change = update_filter)
with col2:
    for i in range((len(slider_keys)+1)//2):
        col2.slider(cgs.qts[slider_dict[slider_keys[i]][0]], 
                    min_value=slider_dict[slider_keys[i]][1], 
                    max_value=slider_dict[slider_keys[i]][2], 
                    value=(slider_dict[slider_keys[i]][1], slider_dict[slider_keys[i]][2]), 
                    key = slider_keys[i], on_change = update_filter)
with col3:
    for i in range((len(slider_keys)+1)//2,len(slider_keys)):
        col3.slider(cgs.qts[slider_dict[slider_keys[i]][0]], 
                    min_value=slider_dict[slider_keys[i]][1], 
                    max_value=slider_dict[slider_keys[i]][2], 
                    value=(slider_dict[slider_keys[i]][1], slider_dict[slider_keys[i]][2]), 
                    key = slider_keys[i], on_change = update_filter)

def foo(widget_instance, payload):
    print(f"{widget_instance} clicked with payload {payload}")

expander_chart = st.expander(f"Hide/show chart", expanded=True)
col1, col2, col3 = expander_chart.columns(3)
with col1:
    xaxis = col1.selectbox("X-axis", cgs.qts.keys(), format_func=lambda x: cgs.qts[x], index=0)
with col2:
    yaxis = col2.selectbox("Y-axis", cgs.qts.keys(), format_func=lambda x: cgs.qts[x], index=1)
with col3:
    group = col3.selectbox("Group", cgs.cats.keys(), format_func=lambda x: cgs.cats[x], index=3)
chart = alt.Chart(st.session_state.df_wide).mark_circle().encode(
    x = alt.X(xaxis, axis=alt.Axis(title=cgs.qts[xaxis])),
    y = alt.Y(yaxis, axis=alt.Axis(title=cgs.qts[yaxis])),
    opacity = alt.value(0.1),
    color = alt.value("gray"),
    tooltip=[alt.Tooltip('name', title='College Name')])
df_filt_rename = st.session_state.df_filt
chart_change = alt.Chart(df_filt_rename).mark_point().encode(
    x = alt.X(xaxis, axis=alt.Axis(title=cgs.qts[xaxis])),
    y = alt.Y(yaxis, axis=alt.Axis(title=cgs.qts[yaxis])),
    color = alt.Color(group, legend=alt.Legend(title=cgs.cats[group],labelLimit=500)),
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