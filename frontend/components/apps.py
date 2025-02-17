import streamlit as st
import pandas as pd
from utils.api import fetch_data

def render_app_filters():
    """Render and return filter values for the apps page."""
    with st.expander("Filters", expanded=True):
        # Filter section
        col1, col2, col3 = st.columns(3)
        with col1:
            name_filter = st.text_input("App Name")
            categories_response = fetch_data("/categories")
            categories = categories_response["data"] if categories_response else None
            category_filter = st.selectbox(
                "Category",
                ["All"] + [c['name'] for c in categories or []]
            )
            content_ratings = ["Everyone", "Teen", "Mature 17+", "Adults only 18+"]
            content_rating_filter = st.selectbox("Content Rating", ["All"] + content_ratings)
            
        with col2:
            is_free_filter = st.selectbox("Price", ["All", "Free", "Paid"])
            min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0)
            sort_by = st.selectbox(
                "Sort by",
                ["None", "Rating", "Rating Count", "Released Date", "Last Updated"]
            )
            
        with col3:
            items_per_page = st.selectbox("Items per page", [100, 200, 500, 100000], index=0)
            sort_order = st.selectbox("Sort Order", ["Descending", "Ascending"])
            st.markdown("###")  # Spacing
            if st.button("Reset Filters"):
                st.rerun()
    
    return {
        "name": name_filter,
        "category": category_filter,
        "content_rating": content_rating_filter,
        "is_free": is_free_filter,
        "min_rating": min_rating,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "items_per_page": items_per_page
    }, categories

def build_query_params(filters, page, categories):
    """Build query parameters for the API request."""
    params = {
        "skip": (page - 1) * filters["items_per_page"],
        "limit": filters["items_per_page"]
    }
    
    if filters["name"]:
        params["name"] = filters["name"]
    if filters["category"] != "All" and categories:
        category_id = next(c['id'] for c in categories if c['name'] == filters["category"])
        params["category_id"] = category_id
    if filters["content_rating"] != "All":
        params["content_rating"] = filters["content_rating"]
    if filters["is_free"] != "All":
        params["is_free"] = filters["is_free"] == "Free"
    if filters["min_rating"] > 0:
        params["min_rating"] = filters["min_rating"]
    if filters["sort_by"] != "None":
        params["sort_by"] = filters["sort_by"].lower().replace(" ", "_")
        params["order"] = "asc" if filters["sort_order"] == "Ascending" else "desc"
    
    return params

def render_apps_page():
    """Main apps page render function."""
    st.subheader("App List")
        
    # Get filters and page number
    page = int(st.query_params.get("page", 1))
    page = st.number_input("Page", min_value=1, value=page)
    filters, categories = render_app_filters()
    
    # Build query parameters
    params = build_query_params(filters, page, categories)
    
    # Fetch filtered apps with loading indicator
    with st.spinner("Loading apps..."):
        apps_response = fetch_data("/apps", params)
        apps = apps_response["data"] if apps_response else None
    
    if apps:
        apps_df = pd.DataFrame(apps)
        
        # Display pagination info
        start_idx = (page - 1) * filters["items_per_page"] + 1
        end_idx = start_idx + len(apps) - 1
        st.write(f"Showing results {start_idx} to {end_idx} ({apps_response['duration_ms']}ms)")
        
        # Display data
        st.dataframe(
            apps_df[[
                'name', 'rating', 'rating_count', 'is_free', 'price',
                'installs', 'content_rating', 'released_date'
            ]],
            use_container_width=True
        )
        
        # Bottom pagination
        col1, col2 = st.columns([1, 8])
        with col1:
            if page > 1:
                if st.button("Previous"):
                    st.query_params["page"] = page-1
                    st.rerun()
        with col2:
            if len(apps) == filters["items_per_page"]:
                if st.button("Next"):
                    st.query_params["page"] = page+1
                    st.rerun()
    else:
        st.info("No apps found matching the criteria")
