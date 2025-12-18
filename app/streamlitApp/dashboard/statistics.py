import streamlit as st
import pandas as pd
import plotly.express as px
from api.client import fetch_stat


def show_top_classes_by_duration():
    st.subheader("📊 Top Classes by Average Meeting Duration")

    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.text_input("Year (optional)", key="duration_year")
    with col2:
        semester = st.selectbox("Semester (optional)",
                                ["", "Fall", "Spring", "V1", "V2"],
                                key="duration_semester")
    with col3:
        limit = st.slider("Number of results", 1, 10, 1, key="duration_limit")

    if st.button("Get Top Classes", key="btn_duration"):
        params = {"limit": limit}
        if year:
            params["year"] = year
        if semester:
            params["semester"] = semester

        data = fetch_stat("stats/top-classes-by-avg-duration", params)

        if data:
            df = pd.DataFrame(data)

            # Bar chart
            fig = px.bar(df, x='fullcode', y='avg_minutes',
                         title=f"Top {limit} Classes by Average Meeting Duration",
                         labels={'avg_minutes': 'Average Minutes', 'fullcode': 'Class'},
                         color='avg_minutes',
                         color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.dataframe(df, use_container_width=True)


def show_classes_without_prereqs():
    st.subheader("📚 Classes Without Prerequisites")

    if st.button("Get Classes", key="btn_prereqs"):
        data = fetch_stat("stats/classes-without-prereqs")

        if data:
            df = pd.DataFrame(data)

            # Count by department
            df['department'] = df['fullcode'].str.extract(r'([A-Z]+)')
            dept_counts = df['department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']

            # Pie chart
            fig = px.pie(dept_counts, values='Count', names='Department',
                         title='Classes Without Prerequisites by Department')
            st.plotly_chart(fig, use_container_width=True)

            # Total count
            st.metric("Total Classes Without Prerequisites", len(df))

            # Data table
            st.dataframe(df, use_container_width=True)


def show_top_rooms_by_utilization():
    st.subheader("🏢 Top Rooms by Utilization")

    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.text_input("Year (optional)", key="util_year")
    with col2:
        semester = st.selectbox("Semester (optional)",
                                ["", "Fall", "Spring", "V1", "V2"],
                                key="util_semester")
    with col3:
        limit = st.slider("Number of results", 1, 10, 5, key="util_limit")

    if st.button("Get Room Utilization", key="btn_util"):
        params = {"limit": limit}
        if year:
            params["year"] = year
        if semester:
            params["semester"] = semester

        data = fetch_stat("stats/top-rooms-by-utilization", params)

        if data:
            df = pd.DataFrame(data)
            df['location'] = df['building'] + ' ' + df['room_number']

            # Bar chart
            fig = px.bar(df, x='location', y='utilization',
                         title=f"Top {limit} Rooms by Utilization Rate",
                         labels={'utilization': 'Utilization Rate', 'location': 'Room'},
                         color='utilization',
                         color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.dataframe(df, use_container_width=True)


def show_multi_room_classes():
    st.subheader("🔄 Multi-Room Classes")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        year = st.text_input("Year (optional)", key="multi_year")
    with col2:
        semester = st.selectbox("Semester (optional)",
                                ["", "Fall", "Spring", "V1", "V2"],
                                key="multi_semester")
    with col3:
        limit = st.slider("Limit", 1, 10, 5, key="multi_limit")
    with col4:
        orderby = st.selectbox("Order", ["desc", "asc"], key="multi_order")

    if st.button("Get Multi-Room Classes", key="btn_multi"):
        params = {"limit": limit, "orderby": orderby}
        if year:
            params["year"] = year
        if semester:
            params["semester"] = semester

        data = fetch_stat("stats/multi-room-classes", params)

        if data:
            df = pd.DataFrame(data)

            # Horizontal bar chart
            fig = px.bar(df, y='fullcode', x='distinct_rooms',
                         orientation='h',
                         title="Classes Using Multiple Rooms",
                         labels={'distinct_rooms': 'Number of Distinct Rooms', 'fullcode': 'Class'},
                         color='distinct_rooms',
                         color_continuous_scale='Oranges')
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.dataframe(df, use_container_width=True)


def show_top_departments():
    st.subheader("🏆 Top Departments by Section Count")

    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.text_input("Year (optional)", key="dept_year")
    with col2:
        semester = st.selectbox("Semester (optional)",
                                ["", "Fall", "Spring", "V1", "V2"],
                                key="dept_semester")
    with col3:
        limit = st.slider("Number of results", 1, 5, 1, key="dept_limit")

    if st.button("Get Top Departments", key="btn_dept"):
        params = {"limit": limit}
        if year:
            params["year"] = year
        if semester:
            params["semester"] = semester

        data = fetch_stat("stats/top-departments-by-sections", params)

        if data:
            df = pd.DataFrame(data)

            # Bar chart
            fig = px.bar(df, x='fullcode', y='sections',
                         title=f"Top {limit} Departments by Number of Sections",
                         labels={'sections': 'Number of Sections', 'fullcode': 'Department'},
                         color='sections',
                         color_continuous_scale='Purples')
            st.plotly_chart(fig, use_container_width=True)

            # Data table
            st.dataframe(df, use_container_width=True)


def show_sections_by_day():
    st.subheader("📅 Sections by Day of Week")

    col1, col2 = st.columns(2)
    with col1:
        year = st.text_input("Year", key="day_year")
    with col2:
        semester = st.selectbox("Semester",
                                ["Fall", "Spring", "V1", "V2"],
                                key="day_semester")

    if st.button("Get Sections by Day", key="btn_day"):
        if year and semester:
            params = {"year": year, "semester": semester}
            data = fetch_stat("stats/sections-by-day", params)

            if data:
                df = pd.DataFrame(data)

                # Line chart
                fig = px.line(df, x='day', y='sections',
                              title=f"Sections by Day - {semester} {year}",
                              markers=True,
                              labels={'count': 'Number of Sections', 'day': 'Day of Week'})
                st.plotly_chart(fig, use_container_width=True)

                # Data table
                st.dataframe(df, use_container_width=True)
        else:
            st.warning("Please enter both year and semester")