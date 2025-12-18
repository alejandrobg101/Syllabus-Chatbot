# Chatbot with REST API and Streamlit Frontend

This project is a **chatbot application** with a REST API backend and a **Streamlit frontend** for interacting with it. It allows users to send queries to the chatbot and receive responses in real-time.

## Features
- REST API backend for chatbot interactions
- Streamlit frontend for a simple and interactive UI
- PDF reader integration for processing documents
- Large Language Model (LLM) based on **LLaMA 3.2**
- Modular and extensible architecture

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
