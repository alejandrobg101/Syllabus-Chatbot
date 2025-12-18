import streamlit as st
from database.db_functions import verify_user, create_user

def login_page():
    st.title("🎓 Course Management System")
    st.markdown("### Login to Access Dashboard")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    user = verify_user(username, password)
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user[1]
                        st.session_state['uid'] = user[0]
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register = st.form_submit_button("Register")
            
            if register:
                if not new_username or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("Passwords don't match")
                elif len(new_password) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    uid = create_user(new_username, new_password)
                    if uid:
                        st.success("Account created! Please login.")
                    else:
                        st.error("Username already exists")