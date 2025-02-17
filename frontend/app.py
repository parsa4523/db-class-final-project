import streamlit as st
from utils.config import setup_page_config
from utils.api import BASE_URL
from components.apps import render_apps_page
from components.categories import render_categories_page
from components.developers import render_developers_page

# Setup page configuration
setup_page_config()

# Sidebar
st.sidebar.text(f"API: {BASE_URL}")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Select Page",
    ["Apps", "Categories", "Developers"]
)

# Title
st.title(f"PlayStore {page}")

if page == "Apps":
    render_apps_page()
elif page == "Categories":
    render_categories_page()
elif page == "Developers":
    render_developers_page()
