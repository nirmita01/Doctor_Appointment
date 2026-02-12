from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Doctor, Appointment

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/add-doctors')
def add_doctors():
    doctors = [
        Doctor(name="Dr. Ram", specialization="Cardiologist"),
        Doctor(name="Dr. Sita", specialization="Dermatologist"),
        Doctor(name="Dr. Hari", specialization="Neurologist")
    ]
    db.session.add_all(doctors)
    db.session.commit()
    return "Doctors added"
