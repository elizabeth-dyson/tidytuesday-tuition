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
        'DC': 'Washington DC',
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

def produce_plot1():
    data_types = {'tc': 'tuition_cost', 'ti': 'tuition_income', 'sp': 'salary_potential', 'ht': 'historical_tuition', 'ds': 'diversity_school'}

    tuition_cost = load_data(data_types['tc'])
    tuition_cost = clean_state_name(tuition_cost)
    salary_potential = load_data(data_types['sp'])
    diversity_school = load_data(data_types['ds'])

    df1 = get_df1(tuition_cost, salary_potential, diversity_school)

    fig = px.scatter(
        df1, x='out_of_state_tuition', y='mid_career_pay', color='state', size='total_enrollment', facet_col='type',
        labels={"in_state_tuition": "In-State Tuition", 'out_of_state_tuition': 'Out-of-State Tuition', "mid_career_pay": "Mid Career Salary", 
                'state': 'State', 'total_enrollment': 'Total Enrollment', 'type': 'Type', 'name': 'School'},
        hover_name='name'
    )
    fig.update_xaxes(matches=None)
    fig.update_yaxes(matches=None)

    return fig

fig = produce_plot1()

st.write(fig)