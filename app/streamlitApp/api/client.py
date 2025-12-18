import streamlit as st
import requests
from api_config import API_BASE_URL
from api_config import API_LOCAL_BASE_URL


def fetch_stat(endpoint, params=None):
    """Generic function to fetch statistics from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/{endpoint}", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

def send_chat_message(question):
    """Send message to chatbot"""
    try:
        response = requests.post(
            f"{API_LOCAL_BASE_URL}/chat",
            json={"question": question}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Error {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}