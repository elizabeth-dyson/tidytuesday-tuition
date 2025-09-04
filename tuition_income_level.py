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


def get_df2():
    data_types = {'tc': 'tuition_cost', 'ti': 'tuition_income', 'sp': 'salary_potential', 'ht': 'historical_tuition', 'ds': 'diversity_school'}

    tuition_cost = load_data(data_types['tc'])
    tuition_income = load_data(data_types['ti'])

    tuition_cost = clean_state_name(tuition_cost)
    tuition_income.loc[tuition_income['income_lvl'] == '48_001 to 75,000', 'income_lvl'] = '48,001 to 75,000'

    sub_cost = tuition_cost[['name', 'state', 'type']].copy()
    sub_income = tuition_income[['name', 'total_price', 'year', 'campus', 'net_cost', 'income_lvl']].copy()

    df2 = pd.merge(sub_income, sub_cost, on='name', how='inner')
    return df2


def set_regions_divisions(df2: pd.DataFrame):
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

    df2['division'] = df2['state'].map(inv_division_dict)
    df2['region'] = df2['division'].map(inv_region_dict)

    return df2


def get_values():
    df2 = get_df2()
    df2 = set_regions_divisions(df2)

    min_year = df2['year'].min()
    max_year = df2['year'].max()

    return min_year, max_year


def get_plot_df(df2: pd.DataFrame, split_col: str):
    df2['percent_cost'] = (df2['net_cost'] / df2['total_price'].mask(lambda x: x == 0)) * 100

    temp_df = df2[(df2['percent_cost'] <= 100) & (df2['percent_cost'] >= 0)].copy()

    temp_df['cost_bin'] = pd.qcut(temp_df['total_price'], q=5)

    temp_df['median'] = temp_df.groupby([split_col, 'income_lvl'])['percent_cost'].transform('median')

    plot_df = temp_df[['income_lvl', 'median', split_col]].drop_duplicates()

    order_dict = {
        '0 to 30,000': 0,
        '30,001 to 48,000': 1,
        '48,001 to 75,000': 2,
        '75,001 to 110,000': 3,
        'Over 110,000': 4
    }

    plot_df['x_order'] = plot_df['income_lvl'].map(order_dict)
    plot_df = plot_df.sort_values(by=[split_col, 'x_order'])
    
    return plot_df


def produce_plot2(chosen_year: int, split_name: str):
    df2 = get_df2()
    df2 = set_regions_divisions(df2)

    df2_year = df2[df2['year'] == chosen_year].copy()

    split_dict = {
        'Region': 'region',
        'Type': 'type',
        'Total Cost': 'cost_bin'
    }

    split_col = split_dict[split_name]
    plot_df = get_plot_df(df2_year, split_col)

    fig = px.line(
        plot_df, x='income_lvl', y='median', color=split_col, labels={"income_lvl": "Income Level", "median": "Median Percentage Paid"}
    )

    return fig


title = st.header("Tuition Cost Percentages by Income Level")

min_year, max_year = get_values()

add_year_slider = st.sidebar.slider(
    'Select Year:', min_year, max_year
)

add_split_selectbox = st.sidebar.selectbox(
    'Group By:', ('Type', 'Region')
)

# add_y_checkbox = st.sidebar.selectbox(
#     'Salary Type:', ('Mid-Career', 'Early Career')
# )

fig2 = produce_plot2(add_year_slider, add_split_selectbox)

chart2 = st.plotly_chart(fig2, use_container_width=True)
