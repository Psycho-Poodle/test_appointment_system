# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_PATH = os.path.join(BASE_DIR, "data", "appointments.db")
CHROMA_PATH = os.path.join(BASE_DIR, "data", "chroma")

# Ensure data directories exist
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(CHROMA_PATH, exist_ok=True)