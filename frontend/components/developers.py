import streamlit as st
import pandas as pd
from utils.api import fetch_data, post_data

def render_developer_filters():
    """Render and return filter values for the developers page."""
    with st.expander("Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            name_filter = st.text_input("Developer Name")
            items_per_page = st.selectbox("Items per page", [100, 200, 500, 100000], index=0)
            
        with col2:
            email_filter = st.text_input("Email")
            if st.button("Reset Filters"):
                st.rerun()
    
    return {
        "name": name_filter,
        "email": email_filter,
        "items_per_page": items_per_page
    }

def build_query_params(filters, page):
    """Build query parameters for the API request."""
    params = {
        "skip": (page - 1) * filters["items_per_page"],
        "limit": filters["items_per_page"]
    }
    
    if filters["name"]:
        params["name"] = filters["name"]
    if filters["email"]:
        params["email"] = filters["email"]
    
    return params

def add_developer_form():
    """Render form for adding a new developer."""
    with st.expander("Add New Developer"):
        with st.form("add_developer"):
            dev_name = st.text_input("Developer Name")
            dev_email = st.text_input("Email")
            dev_website = st.text_input("Website")
            submit = st.form_submit_button("Add Developer")
            
            if submit and dev_name:
                data = {
                    "name": dev_name,
                    "email": dev_email if dev_email else None,
                    "website": dev_website if dev_website else None
                }
                result = post_data("/developers", data)
                if result:
                    st.success("Developer added successfully")
                    st.rerun()
                else:
                    st.error("Failed to add developer")

def render_developers_page():
    """Main developers page render function."""
    st.subheader("Developers")
    
    # Get filters and page number
    page = int(st.query_params.get("page", 1))
    page = st.number_input("Page", min_value=1, value=page)
    filters = render_developer_filters()
    
    # Build query parameters
    params = build_query_params(filters, page)
    
    # Display existing developers
    with st.spinner("Loading developers..."):
        developers_response = fetch_data("/developers", params)
        developers = developers_response["data"] if developers_response else None
    
    if developers:
        # Display pagination info
        start_idx = (page - 1) * filters["items_per_page"] + 1
        end_idx = start_idx + len(developers) - 1
        st.write(f"Showing results {start_idx} to {end_idx} ({developers_response['duration_ms']}ms)")
        
        # Display data
        st.dataframe(pd.DataFrame(developers), use_container_width=True)
        
        # Bottom pagination
        col1, col2 = st.columns([1, 8])
        with col1:
            if page > 1:
                if st.button("Previous"):
                    st.query_params["page"] = page-1
                    st.rerun()
        with col2:
            if len(developers) == filters["items_per_page"]:
                if st.button("Next"):
                    st.query_params["page"] = page+1
                    st.rerun()
    else:
        st.info("No developers found")
    
    # Add new developer form
    add_developer_form()
