from app import db, app
from models import Doctor

with app.app_context():
    doctors = [
        Doctor(name="Dr. Suman Shrestha", specialization="Cardiologist"),
        Doctor(name="Dr. Anish Koirala", specialization="Dermatologist"),
        Doctor(name="Dr. Priyanka Gurung", specialization="Pediatrician"),
        Doctor(name="Dr. Ramesh Adhikari", specialization="Orthopedic Surgeon"),
        Doctor(name="Dr. Sneha Thapa", specialization="Neurologist"),
        Doctor(name="Dr. Bikash Rana", specialization="General Physician"),
        Doctor(name="Dr. Manisha Poudel", specialization="Gynecologist"),
        Doctor(name="Dr. Roshan Bhattarai", specialization="ENT Specialist"),
        Doctor(name="Dr. Aayush Sharma", specialization="Psychiatrist")
    ]

    db.session.add_all(doctors)
    db.session.commit()
