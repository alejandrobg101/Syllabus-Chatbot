import streamlit as st
from dashboard.statistics import (
    show_top_classes_by_duration,
    show_classes_without_prereqs,
    show_top_rooms_by_utilization,
    show_multi_room_classes,
    show_top_departments,
    show_sections_by_day
)
from dashboard.chatbot import chatbot_page

def main_dashboard():
    st.sidebar.title(f"👤 Welcome, {st.session_state['username']}!")
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Statistics Dashboard", "💬 Chatbot"]
    )
    
    if page == "📊 Statistics Dashboard":
        st.title("📊 Course Statistics Dashboard")
        st.markdown("---")
        
        # Create tabs for different statistics
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Duration", "Prerequisites", "Room Utilization", 
            "Multi-Room", "Departments", "By Day"
        ])
        
        with tab1:
            show_top_classes_by_duration()
        
        with tab2:
            show_classes_without_prereqs()
        
        with tab3:
            show_top_rooms_by_utilization()
        
        with tab4:
            show_multi_room_classes()
        
        with tab5:
            show_top_departments()
        
        with tab6:
            show_sections_by_day()
    
    elif page == "💬 Chatbot":
        st.title("💬 Course Assistant Chatbot")
        st.markdown("---")
        chatbot_page()