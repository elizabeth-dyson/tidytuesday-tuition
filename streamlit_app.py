import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


def load_data(data_type: str):
    data = pd.read_csv(f'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2020/2020-03-10/{data_type}.csv')
    return data

def clean_state_name(tuition_cost: pd.DataFrame):
    state_dict = {
        'AS': 'American Samoa',
        'DC': 'District of Columbia',
        'PR': 'Puerto Rico',
        'GU': 'Guam',
        'VI': 'Virgin Islands'
    }

    tuition_cost.loc[tuition_cost['state'].isnull(), 'state'] = tuition_cost.loc[tuition_cost['state'].isnull(), 'state_code'].map(state_dict)
    return tuition_cost

def get_df1(tuition_cost: pd.DataFrame, salary_potential: pd.DataFrame, diversity_school: pd.DataFrame):
    sub_cost = tuition_cost[['name', 'state', 'type', 'degree_length', 'in_state_tuition', 'out_of_state_tuition']].copy()
    sub_sal = salary_potential[['rank', 'name', 'early_career_pay', 'mid_career_pay']].copy()
    sub_div = diversity_school[['name', 'total_enrollment']].copy()

    df_sub = pd.merge(sub_cost, sub_sal, how='inner', on='name')
    df1 = pd.merge(df_sub, sub_div, how='inner', on='name')

    return df1

def set_regions_divisions(df1: pd.DataFrame):
    region_dict = {
        'Northeast': ['New England', 'Middle Atlantic'],
        'Midwest': ['East North Central', 'West North Central'],
        'South': ['South Atlantic', 'East South Central', 'West South Central'],
        'West': ['Mountain', 'Pacific'],
        'Territories': ['Territories']
    }
    division_dict = {
        'New England': ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont'],
        'Middle Atlantic': ['New Jersey', 'New York', 'Pennsylvania'],
        'East North Central': ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin'],
        'West North Central': ['Iowa', 'Kansas', 'Minnesota', 'Missouri', 'Nebraska', 'North Dakota', 'South Dakota'],
        'South Atlantic': ['Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'West Virginia'],
        'East South Central': ['Alabama', 'Kentucky', 'Mississippi', 'Tennessee'],
        'West South Central': ['Arkansas', 'Louisiana', 'Oklahoma', 'Texas'],
        'Moutain': ['Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming'],
        'Pacific': ['Alaska', 'California', 'Hawaii', 'Oregon', 'Washington'],
        'Territories': ['American Samoa', 'Puerto Rico', 'Guam', 'Virgin Islands']
    }

    inv_region_dict = {}
    for key, lis in region_dict.items():
        for div in lis:
            inv_region_dict[div] = key

    inv_division_dict = {}
    for key, lis in division_dict.items():
        for state in lis:
            inv_division_dict[state] = key

    df1['division'] = df1['state'].map(inv_division_dict)
    df1['region'] = df1['division'].map(inv_region_dict)

    return df1

def produce_plot1(color_col: str, x_col: str, y_col: str):
    data_types = {'tc': 'tuition_cost', 'ti': 'tuition_income', 'sp': 'salary_potential', 'ht': 'historical_tuition', 'ds': 'diversity_school'}

    tuition_cost = load_data(data_types['tc'])
    tuition_cost = clean_state_name(tuition_cost)
    salary_potential = load_data(data_types['sp'])
    diversity_school = load_data(data_types['ds'])

    df1 = get_df1(tuition_cost, salary_potential, diversity_school)
    df1 = set_regions_divisions(df1)

    x_dict = {
        'In-State': 'in_state_tuition',
        'Out-of-State': 'out_of_state_tuition'
    }
    y_dict = {
        'Mid-Career': 'mid_career_pay',
        'Early Career': 'early_career_pay'
    }
    color_dict = {
        'State': 'state',
        'Degree Length': 'degree_length',
        'Region': 'region',
        'Regional Division': 'division'
    }

    fig = px.scatter(
        df1, x=x_dict[x_col], y=y_dict[y_col], color=color_dict[color_col], size='total_enrollment', facet_col='type',
        labels={"in_state_tuition": "In-State Tuition", 'out_of_state_tuition': 'Out-of-State Tuition', "mid_career_pay": "Mid Career Salary", 'region': 'Region',
                'state': 'State', 'total_enrollment': 'Total Enrollment', 'type': 'Type', 'name': 'School', 'early_career_pay': 'Early Career Salary', 'division': 'Regional Division'},
        hover_name='name'
    )
    fig.update_xaxes(matches=None)
    fig.update_yaxes(matches=None)
    fig.update_layout(height=600, margin=dict(l=20,r=20,t=40,b=20))

    return fig

title = st.header("Tuition Cost & Salaries")

st.set_page_config(layout="wide")

add_color_checkbox = st.sidebar.selectbox(
    'Color By:', ('State', 'Degree Length', 'Region', 'Regional Division')
)

add_x_checkbox = st.sidebar.selectbox(
    'Tuition Type:', ('In-State', 'Out-of-State')
)

add_y_checkbox = st.sidebar.selectbox(
    'Salary Type:', ('Mid-Career', 'Early Career')
)

fig1 = produce_plot1(add_color_checkbox, add_x_checkbox, add_y_checkbox)

chart1 = st.plotly_chart(fig1, use_container_width=True)

