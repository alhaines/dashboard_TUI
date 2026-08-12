#!/home/al/miniconda3/envs/py/bin/python3

import os
import pymysql

# Database credentials
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = 'PassWord'

# Database configurations for different services
# Main menu database (users, siteslinks, contacts, etc.)
db_mainmenu = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': 'main'
}

APIKEY = "" # Gemini AI API KEY

# Flask session configuration
SECRET_KEY = '' # used ny flask

