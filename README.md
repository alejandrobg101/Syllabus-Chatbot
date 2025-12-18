# Chatbot with REST API and Streamlit Frontend

This project is a **chatbot application** with a REST API backend and a **Streamlit frontend** for interacting with it. It allows users to send queries to the chatbot and receive responses in real-time.

## Features
- REST API backend for chatbot interactions
- Streamlit frontend for a simple and interactive UI
- PDF reader integration for processing documents
- Large Language Model (LLM) based on **LLaMA 3.2**
- Modular and extensible architecture

---

## Database Configuration

For personal use, you need to provide your own database configuration. The project uses PostgreSQL and expects a `db_config` dictionary like this:

```python
# Database configuration information
db_config = {
    'user': '<your_db_user>',
    'passwd': '<your_db_password>',
    'dbname': '<your_db_name>',
    'host': '<your_db_host>',
    'port': '<your_db_port>'
}
```
## Tables
### class

-Stores information about courses.

```sql
CREATE TABLE IF NOT EXISTS class (
    cid       SERIAL PRIMARY KEY,
    cname     VARCHAR,
    ccode     VARCHAR,
    cdesc     VARCHAR,
    term      VARCHAR,
    years     VARCHAR,
    cred      INTEGER,
    csyllabus VARCHAR
);
```
### meeting

- Stores class meeting times.

```sql
CREATE TABLE IF NOT EXISTS meeting (
    mid       SERIAL PRIMARY KEY,
    ccode     VARCHAR,
    starttime TIME,
    endtime   TIME,
    cdays     VARCHAR(5)
);
```

### requisite

- Stores prerequisite relationships between classes.

```sql
CREATE TABLE IF NOT EXISTS requisite (
    classid INTEGER NOT NULL REFERENCES public.class,
    reqid   INTEGER NOT NULL REFERENCES public.class,
    prereq  BOOLEAN,
    PRIMARY KEY (classid, reqid)
);
```

### room

- Stores information about classrooms.

```sql
CREATE TABLE IF NOT EXISTS room (
    rid         SERIAL PRIMARY KEY,
    building    VARCHAR,
    room_number VARCHAR,
    capacity    INTEGER
);
```

### section

- Stores specific sections of classes with assigned rooms and meetings.

```sql
CREATE TABLE IF NOT EXISTS section (
    sid      SERIAL PRIMARY KEY,
    roomid   INTEGER REFERENCES public.room,
    cid      INTEGER REFERENCES public.class,
    mid      INTEGER REFERENCES public.meeting,
    semester VARCHAR,
    years    VARCHAR,
    capacity INTEGER
);
```

### syllabus

- Stores chunks of course syllabi with embeddings for LLM queries.

```sql
CREATE TABLE IF NOT EXISTS syllabus (
    chunkid        SERIAL PRIMARY KEY,
    courseid       INTEGER REFERENCES public.class,
    embedding_text VECTOR(768),
    chunk          VARCHAR
);
```

### users

- Stores registered user credentials for authentication.

```sql
CREATE TABLE IF NOT EXISTS users (
    uid      SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### Usage Notes

- Make sure your db_config dictionary points to your PostgreSQL database.

- The chatbot will read course information from class, section, and syllabus.

- Prerequisites are stored in requisite to answer queries about course dependencies.

- users can be used for authentication if you expand the chatbot with user accounts.

## Running the Project

Before using the Streamlit frontend, make sure the backend is running.

- Step 1: Run the REST API

-- Start the main chatbot backend:

```bash
python main.py

```

-- Start the file handler for PDF processing:

```bash
python filehandler.py
```

-- Both scripts should remain running while using the Streamlit app. They provide the API endpoints the frontend relies on.

-Step 2: Run the Streamlit Frontend

-- In a new terminal, navigate to the project folder and run:

```bash
streamlit run app.py
```

-- This will launch the Streamlit interface in your default web browser.

-- You can interact with the chatbot in real-time and upload PDFs to be processed by the backend.

### Additional Notes

- Ensure your PostgreSQL database is running before starting the backend.

- Always start the backend scripts before opening the Streamlit app.

- Streamlit automatically reloads when you make changes to the frontend code.

- Do not commit your virtual environment (ven) to GitHub.

- Use placeholders in db_config for sensitive information.
