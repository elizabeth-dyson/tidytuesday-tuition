import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

salary_page = st.Page("tuition_salary.py", title="Salary v Tuition", icon=":material/attach_money:")

pg = st.navigation([salary_page])
st.set_page_config(page_title="Tuition Data Viewer", page_icon=":material/school:")

pg.run()