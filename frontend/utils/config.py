import streamlit as st

# Page configuration
def setup_page_config():
    st.set_page_config(
        page_title="PlayStore Apps Dashboard",
        page_icon="🎮",
        layout="wide"
    )

# Constants
CONTENT_RATING_OPTIONS = [
    "All",
    "Everyone",
    "Teen",
    "Everyone 10+",
    "Mature 17+",
    "Adults only 18+"
]

PRICE_OPTIONS = ["All", "Free", "Paid"]

# API Configuration
API_BASE_URLS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000"
]

# Pagination settings
ITEMS_PER_PAGE = 10
