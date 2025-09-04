import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import re


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


def get_df(type_list: np.array, length_list: np.array, data_choice: str):
    data_types = {'tc': 'tuition_cost', 'ti': 'tuition_income', 'sp': 'salary_potential', 'ht': 'historical_tuition', 'ds': 'diversity_school'}
    tuition_cost = load_data(data_types['tc'])
    salary_potential = load_data(data_types['sp'])
    diversity_school = load_data(data_types['ds'])

    tuition_cost = clean_state_name(tuition_cost)
    tuition_cost = set_regions_divisions(tuition_cost)

    filt_tuition_cost = tuition_cost[(tuition_cost['type'].isin(type_list)) & (tuition_cost['degree_length'].isin(length_list))].reset_index(drop=True)

    if data_choice in ["Early Career Pay", "Mid Career Pay"]:
        choice = re.sub(r"\s", "_", data_choice.lower())
        salary_potential = salary_potential[['name', choice]].copy()
        filt_salary_potential = salary_potential[salary_potential['name'].isin(filt_tuition_cost['name'].unique())].reset_index(drop=True)
        filt_tuition_cost = filt_tuition_cost[['name', 'state_code']].copy()

        df = pd.merge(filt_tuition_cost, filt_salary_potential, how="inner", on="name")
        df['avg_choice'] = df.groupby('state_code')[choice].transform('mean')
        stat_df = df[['state_code', 'avg_choice']].drop_duplicates().reset_index(drop=True)

    elif data_choice in ["Race", "Gender"]:
        diversity_school = diversity_school.drop(columns=['state'])
        filt_diversity_school = diversity_school[diversity_school['name'].isin(filt_tuition_cost['name'].unique())].reset_index(drop=True)
        filt_tuition_cost = filt_tuition_cost[['name', 'state_code']].copy()
        df = pd.merge(filt_tuition_cost, filt_diversity_school, how='inner', on='name')

        if data_choice == 'Gender':
            df = df[df['category'] == 'Women'].reset_index(drop=True)

            # men_rows = []
            # for _, row in df.iterrows():
            #     men_enrollment = row['total_enrollment'] - row['enrollment']
            #     temp_df = pd.DataFrame({
            #         'name': row['name'],
            #         'total_enrollment': row['total_enrollment'],
            #         'state': row['state'],
            #         'category': ['Men'],
            #         'enrollment': [men_enrollment]
            #     })
            #     men_rows.append(temp_df)

            # df = pd.concat([df] + men_rows, ignore_index=True).sort_values(by='name').reset_index(drop=True)

        else:
            df = df[df['category'] == 'Total Minority'].reset_index(drop=True)

        df['enrollment_percent'] = (df['enrollment'] / df['total_enrollment']) * 100
        df['avg_choice'] = df.groupby('state_code')['enrollment_percent'].transform('mean')
        stat_df = df[['state_code', 'avg_choice']].drop_duplicates().reset_index(drop=True)

    else:
        cost_dict = {
            "Out-of-State Tuition": "out_of_state_tuition",
            "In-State Tuition": "in_state_tuition",
            "Room & Board": "room_and_board"
        }

        choice = cost_dict[data_choice]
        df = filt_tuition_cost[['name', 'state_code', choice]].copy()
        df['avg_choice'] = df.groupby('state_code')[choice].transform('mean')
        stat_df = df[['state_code', 'avg_choice']].drop_duplicates().reset_index(drop=True)

    return stat_df


def produce_plot(type_list: np.array, length_list: np.array, data_choice: str):
    df = get_df(type_list, length_list, data_choice)

    fig = px.choropleth(locations=df['state_code'], locationmode="USA-states", color=df['avg_choice'], scope="usa", labels={"color": data_choice})
    fig.update_geos(
        scope="usa",
        projection=dict(type="albers usa"),
        showcoastlines=False,
        showcountries=False
    )

    return fig


title = st.header("Statistics by State")

filter_type_multiselect = st.sidebar.multiselect(
    "Filter School Type:", ("Public", "Private", "For Profit"), default=["Public", "Private", "For Profit"]
)

filter_length_multiselect = st.sidebar.multiselect(
    "Filter Degree Length:", ("4 Year", "2 Year"), default=["4 Year", "2 Year"]
)

choose_data_selectbox = st.sidebar.selectbox(
    "Show Statistics About:", ( "Out-of-State Tuition", "In-State Tuition", "Room & Board", "Early Career Pay", "Mid Career Pay", "Race", "Gender")
)

fig = produce_plot(filter_type_multiselect, filter_length_multiselect, choose_data_selectbox)

chart = st.plotly_chart(fig, use_container_width=True)