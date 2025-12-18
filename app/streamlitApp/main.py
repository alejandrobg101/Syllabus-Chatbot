import streamlit as st
from api_config import API_BASE_URL
from auth.login import login_page
from dashboard.main_dashboard import main_dashboard
from database.db_functions import init_user_table

def main():
    st.set_page_config(
        page_title="Course Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_user_table()
    
    # Check login status
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()