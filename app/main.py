# app/main.py
from app.database import init_db
from app.appointment_system import AppointmentSystem
from app.config import GROQ_API_KEY, DATABASE_PATH, CHROMA_PATH

def main():
    # Initialize database
    init_db()
    
    # Create appointment system instance
    appointment_system = AppointmentSystem(
        db_path=DATABASE_PATH,
        chroma_path=CHROMA_PATH,
        groq_api_key=GROQ_API_KEY
    )
    
    # Example usage
    result = appointment_system.book_appointment(
        date="2025-02-24",
        time="14:00",
        user_id="user123",
        description="Regular medical checkup"
    )
    print(result)

if __name__ == "__main__":
    main()