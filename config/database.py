import os
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from datetime import datetime

# Charger les variables d'environnement
load_dotenv()

# Initialisation de SQLAlchemy
db = SQLAlchemy()

# Construction de l'URI MySQL
DB_USER = os.getenv('DB_USER', 'user_name')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'your_password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'BLOG')

# Format URI MySQL : mysql+pymysql://user:password@host:port/database
DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
