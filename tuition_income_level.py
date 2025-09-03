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


def find_first_quartile(data):
    return data.quantile(0.25)

def find_third_quartile(data):
    return data.quantile(0.75)


def get_plot_df(df2: pd.DataFrame, facet_col: str = None):
    df2['percent_cost'] = (df2['net_cost'] / df2['total_price'].mask(lambda x: x == 0)) * 100

    temp_df = df2[(df2['percent_cost'] <= 100) & (df2['percent_cost'] >= 0)].copy()

    if facet_col == 'total_cost':
        max_cost = temp_df['total_price'].max()
        min_cost = temp_df['total_price'].min()
        interval = round((max_cost - min_cost) / 5)
        bin_maxs = [min_cost + i * interval for i in range(1,6)]
        temp_df['cost_bin'] = None

        for i in range(4):
            if i == 0:
                lo = 0
                hi = bin_maxs[0]
            else:
                lo = bin_maxs[i]
                hi = bin_maxs[i+1]

            for j, row in temp_df.iterrows():
                row_cost = row['total_price']
                row_bin = row['cost_bin']
                if not row_bin:
                    if row_cost <= hi & row_cost > lo:
                        temp_df.loc[j, 'cost_bin'] = f'${lo}-${hi}'

        facet_col = 'cost_bin'

    if facet_col:
        temp_df['median'] = temp_df.groupby([facet_col, 'income_lvl'])['percent_cost'].transform('median')
        temp_df['q1'] = temp_df.groupby([facet_col, 'income_lvl'])['percent_cost'].transform(find_first_quartile)
        temp_df['q3'] = temp_df.groupby([facet_col, 'income_lvl'])['percent_cost'].transform(find_third_quartile)
    else:
        temp_df['median'] = temp_df.groupby('income_lvl')['percent_cost'].transform('median')
        temp_df['q1'] = temp_df.groupby('income_lvl')['percent_cost'].transform(find_first_quartile)
        temp_df['q3'] = temp_df.groupby('income_lvl')['percent_cost'].transform(find_third_quartile)

    temp_df['e_plus'] = temp_df['q3'] - temp_df['median']
    temp_df['e_minus'] = temp_df['median'] - temp_df['q1']

    if facet_col:
        plot_df = temp_df[['income_lvl', 'median', 'e_plus', 'e_minus', facet_col]].drop_duplicates()
    else:
        plot_df = temp_df[['income_lvl', 'median', 'e_plus', 'e_minus']].drop_duplicates()

    return plot_df


def produce_plot2(chosen_year: int, facet_name: str):
    df2 = get_df2()
    df2 = set_regions_divisions(df2)

    df2_year = df2[df2['year'] == chosen_year].copy()

    facet_dict = {
        'None': None,
        'Region': 'region',
        'Type': 'type',
        'Total Cost': 'total_cost'
    }

    facet_col = facet_dict[facet_name]
    plot_df = get_plot_df(df2_year, facet_col)

    if facet_col:
        fig = px.bar(
            plot_df, x='income_lvl', y='median', error_y='e_plus', error_y_minus='e_minus',
            labels={"median": "Percentage Paid of Total Cost", "income_lvl": "Income Level",
                    "type": "Type", "total_cost": "Total Cost"},
            facet_row=facet_col
        )
    else:
        fig = px.bar(
            plot_df, x='income_lvl', y='median', error_y='e_plus', error_y_minus='e_minus',
            labels={"median": "Percentage Paid of Total Cost", "income_lvl": "Income Level",
                    "type": "Type", "total_cost": "Total Cost"}
        )

    return fig


title = st.header("Tuition Cost Percentages by Income Level")

min_year, max_year = get_values()

add_year_slider = st.sidebar.slider(
    'Select Year:', min_year, max_year
)

add_facet_selectbox = st.sidebar.selectbox(
    'Group By:', ('None', 'Region', 'Type', 'Total Cost')
)

# add_y_checkbox = st.sidebar.selectbox(
#     'Salary Type:', ('Mid-Career', 'Early Career')
# )

fig2 = produce_plot2(add_year_slider, add_facet_selectbox)

chart2 = st.plotly_chart(fig2, use_container_width=True)
