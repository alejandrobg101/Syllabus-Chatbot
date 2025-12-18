import streamlit as st
import psycopg2
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.dbconfig import pg_config

def init_user_table():
    """Create users table if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            dbname=pg_config['dbname'],
            user=pg_config['user'],
            password=pg_config['passwd'],
            host=pg_config['host'],
            port=pg_config['port']
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        st.error(f"Database error: {e}")

def verify_user(username, password):
    """Verify user credentials"""
    try:
        conn = psycopg2.connect(
            dbname=pg_config['dbname'],
            user=pg_config['user'],
            password=pg_config['passwd'],
            host=pg_config['host'],
            port=pg_config['port']
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT uid, username FROM users WHERE username = %s AND password = %s",
            (username, password)
        )
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def create_user(username, password):
    """Create a new user"""
    try:
        conn = psycopg2.connect(
            dbname=pg_config['dbname'],
            user=pg_config['user'],
            password=pg_config['passwd'],
            host=pg_config['host'],
            port=pg_config['port']
        )
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s) RETURNING uid",
            (username, password)
        )
        uid = cursor.fetchone()[0]
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return uid
    except psycopg2.IntegrityError:
        return None
    except Exception as e:
        st.error(f"Registration error: {e}")
        return None