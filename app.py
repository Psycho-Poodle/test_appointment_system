# app.py
import streamlit as st
from app.database import init_db
from app.appointment_system import AppointmentSystem
from app.config import GROQ_API_KEY, DATABASE_PATH, CHROMA_PATH

# Initialize the database and appointment system
init_db()
appointment_system = AppointmentSystem(
    db_path=DATABASE_PATH,
    chroma_path=CHROMA_PATH,
    groq_api_key=GROQ_API_KEY
)

# Streamlit App
st.title("Appointment Booking System")

# Input fields for booking an appointment
st.header("Book an Appointment")
date = st.date_input("Select Date")
time = st.time_input("Select Time")
user_id = st.text_input("User ID")
description = st.text_area("Description")

# Book appointment button
if st.button("Book Appointment"):
    if not date or not time or not user_id or not description:
        st.error("Please fill in all fields.")
    else:
        result = appointment_system.book_appointment(
            date=str(date),
            time=str(time),
            user_id=user_id,
            description=description
        )
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])

# Find similar appointments
st.header("Find Similar Appointments")
query = st.text_input("Enter a query to find similar appointments")
if st.button("Search"):
    if not query:
        st.error("Please enter a query.")
    else:
        results = appointment_system.find_similar_appointments(query)
        st.write(results)

# Get appointment suggestions using Groq
st.header("Get Appointment Suggestions")
user_query = st.text_input("Enter your query for suggestions")
if st.button("Get Suggestions"):
    if not user_query:
        st.error("Please enter a query.")
    else:
        suggestions = appointment_system.get_appointment_suggestions(user_query)
        st.write(suggestions)