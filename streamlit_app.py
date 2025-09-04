import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

salary_page = st.Page("tuition_salary.py", title="Salary v Tuition", icon=":material/attach_money:")
income_level_page = st.Page("tuition_income_level.py", title="Tuition Cost by Income Level", icon=":material/attach_money:")
diversity_page = st.Page("diversity.py", title="Diversity Statistics", icon=":material/diversity_1:")
map_page = st.Page("us_map.py", title="Statistics by State", icon=":material/location_on:")

pg = st.navigation([salary_page, income_level_page, diversity_page, map_page])
st.set_page_config(page_title="Tuition Data Viewer", page_icon=":material/school:", layout="wide")

pg.run()