import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


def load_data(data_type: str):
    data = pd.read_csv(f'https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2020/2020-03-10/{data_type}.csv')
    return data


def set_regions_divisions(df: pd.DataFrame):
    region_dict = {
        'Northeast': ['New England', 'Middle Atlantic'],
        'Midwest': ['East North Central', 'West North Central'],
        'South': ['South Atlantic', 'East South Central', 'West South Central'],
        'West': ['Mountain', 'Pacific']
    }
    division_dict = {
        'New England': ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont'],
        'Middle Atlantic': ['New Jersey', 'New York', 'Pennsylvania'],
        'East North Central': ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin'],
        'West North Central': ['Iowa', 'Kansas', 'Minnesota', 'Missouri', 'Nebraska', 'North Dakota', 'South Dakota'],
        'South Atlantic': ['Delaware', 'District of Columbia', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'West Virginia'],
        'East South Central': ['Alabama', 'Kentucky', 'Mississippi', 'Tennessee'],
        'West South Central': ['Arkansas', 'Louisiana', 'Oklahoma', 'Texas'],
        'Mountain': ['Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming'],
        'Pacific': ['Alaska', 'California', 'Hawaii', 'Oregon', 'Washington']
    }

    inv_region_dict = {}
    for key, lis in region_dict.items():
        for div in lis:
            inv_region_dict[div] = key

    inv_division_dict = {}
    for key, lis in division_dict.items():
        for state in lis:
            inv_division_dict[state] = key

    df['division'] = df['state'].map(inv_division_dict)
    df['region'] = df['division'].map(inv_region_dict)

    return df


def get_dfs(div_type: str):
    data_types = {'tc': 'tuition_cost', 'ti': 'tuition_income', 'sp': 'salary_potential', 'ht': 'historical_tuition', 'ds': 'diversity_school'}

    tuition_cost = load_data(data_types['tc'])
    diversity_school = load_data(data_types['ds'])

    sub_cost = tuition_cost[['name', 'type', 'degree_length']].copy()

    df_sub = pd.merge(sub_cost, diversity_school, how='inner', on='name')
    df_sub = set_regions_divisions(df_sub)

    df_sub['enrollment_percent'] = (df_sub['enrollment'] / df_sub['total_enrollment']) * 100

    if div_type == 'Gender':
        df = df_sub[df_sub['category'] == 'Women'].reset_index(drop=True)

        men_rows = []
        for _, row in df.iterrows():
            men_enrollment = row['total_enrollment'] - row['enrollment']
            temp_df = pd.DataFrame({
                'name': row['name'],
                'total_enrollment': row['total_enrollment'],
                'state': row['state'],
                'category': ['Men'],
                'enrollment': [men_enrollment],
                'type': row['type'],
                'degree_length': row['degree_length'],
                'division': row['division'],
                'region': row['region']
            })
            men_rows.append(temp_df)

        df = pd.concat([df] + men_rows, ignore_index=True).sort_values(by='name').reset_index(drop=True)

    else:
        df = df_sub[(df_sub['category'] != 'Women') & (df_sub['category'] != 'Total Minority')].reset_index(drop=True)

    df['enrollment_percent'] = (df['enrollment'] / df['total_enrollment']) * 100
    df['avg_percent'] = df.groupby(['region', 'category'])['enrollment_percent'].transform('mean')
    stat_df = df[['category', 'region', 'avg_percent']].drop_duplicates().reset_index(drop=True)

    return stat_df


def produce_plot(div_type: str):
    div_df = get_dfs(div_type)

    # x_dict = {
    #     'In-State': 'in_state_tuition',
    #     'Out-of-State': 'out_of_state_tuition'
    # }
    # y_dict = {
    #     'Mid-Career': 'mid_career_pay',
    #     'Early Career': 'early_career_pay'
    # }
    # color_dict = {
    #     'State': 'state',
    #     'Degree Length': 'degree_length',
    #     'Region': 'region',
    #     'Regional Division': 'division'
    # }

    fig = px.bar(div_df, x='region', y='enrollment_percent', color='category')

    return fig

title = st.header("Diversity Statistics")

choose_div_selectbox = st.sidebar.selectbox(
    'Diversity Type:', ('Gender', 'Race')
)

# add_color_checkbox = st.sidebar.selectbox(
#     'Color By:', ('State', 'Degree Length', 'Region', 'Regional Division')
# )

# add_x_checkbox = st.sidebar.selectbox(
#     'Tuition Type:', ('Out-of-State', 'In-State')
# )

# add_y_checkbox = st.sidebar.selectbox(
#     'Salary Type:', ('Mid-Career', 'Early Career')
# )

fig = produce_plot(choose_div_selectbox)

chart = st.plotly_chart(fig, use_container_width=True)