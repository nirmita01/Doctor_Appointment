from app import db, app
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()  # drops any existing tables
    db.create_all()  # creates tables fresh
    
    admin_user = User(
        name="Nirmita Pandit",
        email="nirmita@gmail.com",
        password=generate_password_hash("Admin@123", method='pbkdf2:sha256'),
        is_admin=True
    )
    db.session.add(admin_user)
    db.session.commit()
