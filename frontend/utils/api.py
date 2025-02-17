import requests
import streamlit as st
import time
from .config import API_BASE_URLS

def get_working_api_url():
    """Try different localhost variants to find a working API endpoint."""
    for url in API_BASE_URLS:
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                return url
        except:
            continue
    return API_BASE_URLS[0]  # Default to localhost if none work

# Initialize base URLs
BASE_URL = get_working_api_url()
API_URL = f"{BASE_URL}/api/v1"

def fetch_data(endpoint: str, params=None):
    """Generic function to fetch data from the API."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", params=params)
        response.raise_for_status()
        response_data = response.json()
        return {
            "data": response_data["data"],
            "duration_ms": response_data["metadata"]["query_duration_ms"]
        }
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {API_URL}")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def post_data(endpoint: str, data: dict):
    """Generic function to post data to the API."""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data)
        response.raise_for_status()
        response_data = response.json()
        return {
            "data": response_data["data"],
            "duration_ms": response_data["metadata"]["query_duration_ms"]
        }
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {API_URL}")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP Error: {e}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def check_api_health():
    """Check if the API is healthy and accessible."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        health = response.json()
        if health.get("status") == "healthy":
            st.success("API is connected and healthy")
            return True
        else:
            st.error(f"API is not healthy: {health}")
            return False
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {BASE_URL}")
        return False
    except Exception as e:
        st.error(f"Error checking API health: {str(e)}")
        return False
