# app/appointment_system.py
import sqlite3
import chromadb
import os
from datetime import datetime
from groq import Groq
from typing import Optional, Dict, List

class AppointmentSystem:
    def __init__(self, db_path: str = "appointments.db", 
                 chroma_path: str = "data/chroma",
                 groq_api_key: str = None):
        # Ensure ChromaDB directory exists
        os.makedirs(chroma_path, exist_ok=True)
        
        # Initialize SQLite
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._setup_database()  # Call the setup_database method
        
        # Initialize ChromaDB with persistent storage
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        
        # Create or get existing collection
        try:
            self.collection = self.chroma_client.get_collection(name="appointments")
        except ValueError:  # Collection does not exist
            self.collection = self.chroma_client.create_collection(name="appointments")
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=groq_api_key)

    def _setup_database(self):
        """Create appointments table if it doesn't exist"""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            user_id TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def is_slot_available(self, date: str, time: str) -> bool:
        """Check if a time slot is available"""
        self.cursor.execute("""
        SELECT COUNT(*) FROM appointments 
        WHERE date = ? AND time = ?
        """, (date, time))
        count = self.cursor.fetchone()[0]
        return count == 0

    def book_appointment(self, date: str, time: str, user_id: str, description: str) -> Dict:
        """Book an appointment if the slot is available"""
        if not self.is_slot_available(date, time):
            return {
                "success": False,
                "message": f"The slot on {date} at {time} is already taken. Please choose another time."
            }

        try:
            # Add to SQLite
            self.cursor.execute("""
            INSERT INTO appointments (date, time, user_id, description)
            VALUES (?, ?, ?, ?)
            """, (date, time, user_id, description))
            
            appointment_id = self.cursor.lastrowid
            self.conn.commit()

            # Add to ChromaDB for semantic search
            self.collection.add(
                documents=[description],
                metadatas=[{"date": date, "time": time, "user_id": user_id}],
                ids=[str(appointment_id)]
            )

            return {
                "success": True,
                "message": f"Appointment successfully booked for {date} at {time}",
                "appointment_id": appointment_id
            }
        except Exception as e:
            self.conn.rollback()
            return {
                "success": False,
                "message": f"Error booking appointment: {str(e)}"
            }

    def find_similar_appointments(self, query: str, n_results: int = 5) -> List[Dict]:
        """Find similar appointments using ChromaDB"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results

    def get_appointment_suggestions(self, user_query: str) -> str:
        """Use Groq to generate appointment suggestions"""
        prompt = f"""Based on the following user query, suggest appropriate 
        appointment times and provide helpful recommendations: {user_query}"""
        
        completion = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            max_tokens=500
        )
        return completion.choices[0].message.content

    def __del__(self):
        """Clean up database connection"""
        self.conn.close()