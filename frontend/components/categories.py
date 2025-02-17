import streamlit as st
import pandas as pd
from utils.api import fetch_data, post_data
import plotly.graph_objects as go

def add_category_form():
    """Render form for adding a new category."""
    with st.expander("Add New Category"):
        with st.form("add_category"):
            category_name = st.text_input("Category Name")
            submit = st.form_submit_button("Add Category")
            
            if submit and category_name:
                result = post_data("/categories", {"name": category_name})
                if result:
                    st.success("Category added successfully")
                    st.rerun()
                else:
                    st.error("Failed to add category")

def render_yearly_stats(category_id, category_name):
    """Render yearly statistics chart for a category."""
    stats_response = fetch_data(f"/apps/yearly-stats/{category_id}")
    if not stats_response:
        st.warning(f"No data available for category: {category_name}")
        return

    stats = stats_response.get("data", {})

    # Get all years from both released and updated stats
    all_years = sorted(set(
        list(stats['released'].keys()) + 
        list(stats['updated'].keys())
    ))
    
    # Prepare data for plotting
    released_counts = [stats['released'].get(year, 0) for year in all_years]
    updated_counts = [stats['updated'].get(year, 0) for year in all_years]
    
    # Create the bar chart
    fig = go.Figure(data=[
        go.Bar(
            name='Released Apps',
            x=all_years,
            y=released_counts,
            marker_color='#1f77b4'
        ),
        go.Bar(
            name='Updated Apps',
            x=all_years,
            y=updated_counts,
            marker_color='#2ca02c'
        )
    ])
    
    # Update layout
    fig.update_layout(
        title=f'Yearly Statistics for {category_name} ({stats_response.get("duration_ms", 0)}ms)',
        xaxis_title='Year',
        yaxis_title='Number of Apps',
        barmode='group',
        showlegend=True,
        hovermode='x unified'
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

def render_categories_page():
    """Main categories page render function."""
    
    categories_response = fetch_data("/categories")
    # Get category list for the stats selector
    categories = categories_response["data"] if categories_response else None
    if categories:
        st.subheader(f"Category Statistics")
        selected_category = st.selectbox(
            f"Select Category for Statistics",
            options=[c['name'] for c in categories],
            key="stats_category"
        )
        
    # Get category ID for the selected category
    category_id = next(c['id'] for c in categories if c['name'] == selected_category)
    
    # Get and display average rating
    rating_stats_response = fetch_data(f"/categories/{category_id}/rating")
    if rating_stats_response:
        rating_stats = rating_stats_response["data"]
        avg_rating = rating_stats["average_rating"]
        st.metric(
            label=f"Average Rating in {selected_category} ({rating_stats_response.get('duration_ms', 0)}ms)",
            value=f"⭐ {avg_rating:.2f}/5.00"
        )
    
    render_yearly_stats(category_id, selected_category)
    
    st.divider()  # Visual separator between sections

    st.subheader("Categories")

    categories = categories_response["data"] if categories_response else None
    if categories:
        st.caption(f"Categories loaded in {categories_response.get('duration_ms', 0)}ms")
        st.dataframe(pd.DataFrame(categories), use_container_width=True)
    else:
        st.info("No categories found")

    
    st.divider()  # Visual separator between sections
    
    # Add new category form
    add_category_form()
