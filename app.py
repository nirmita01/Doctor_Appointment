from flask import Flask, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Doctor, Appointment
from config import Config
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# ---------------- Create Tables ----------------
with app.app_context():
    db.create_all()

# ---------------- Flask-Admin ----------------
class AdminModelView(ModelView):
    def is_accessible(self):
        return session.get('is_admin')

    def inaccessible_callback(self, name, **kwargs):
        flash("Admins only!", "danger")
        return redirect(url_for('login'))

admin = Admin(app, name="Doctor System", template_mode='bootstrap3')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Doctor, db.session))
admin.add_view(AdminModelView(Appointment, db.session))


# ---------------- Home ----------------
@app.route('/')
def home():
    doctors = Doctor.query.all()
    return render_template('index.html', doctors=doctors)


# ---------------- Register ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        user = User(name=name, email=email, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# ---------------- Login ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        if session.get('is_admin'):
         return redirect(url_for('admin_dashboard'))

        else:
            return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'user')  # Default to user

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            # Check role
            if role == 'admin' and not user.is_admin:
                flash("This account is not an admin.", "danger")
                return redirect(url_for('login'))
            if role == 'user' and user.is_admin:
                flash("Please select Admin login for this account.", "warning")
                return redirect(url_for('login'))
            
            # Set session
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['is_admin'] = user.is_admin

            flash(f"Welcome, {user.name}!", "success")
            return redirect(url_for('admin_dashboard') if user.is_admin else url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# ---------------- Dashboard ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    doctors = Doctor.query.all()
    return render_template('dashboard.html', doctors=doctors)

# ---------------- Admin Dashboard ----------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('login'))

    total_doctors = Doctor.query.count()
    total_patients = User.query.filter_by(is_admin=False).count()
    total_appointments = Appointment.query.count()

    upcoming_appointments = Appointment.query.order_by(Appointment.date).limit(5).all()

    return render_template(
        'admin_dashboard.html',
        total_doctors=total_doctors,
        total_patients=total_patients,
        total_appointments=total_appointments,
        upcoming_appointments=upcoming_appointments
    )

# ---------------- Admin: View Doctors ----------------
@app.route('/admin/doctors')
def admin_doctors():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    doctors = Doctor.query.all()
    return render_template('admin_doctors.html', doctors=doctors)

# ---------------- Admin: View Patients ----------------
@app.route('/admin/patients')
def admin_patients():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    patients = User.query.filter_by(is_admin=False).all()
    return render_template('admin_patients.html', patients=patients)

# ---------------- Admin: View Appointments ----------------
@app.route('/admin/appointments')
def admin_appointments():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    appointments = Appointment.query.order_by(Appointment.date).all()
    return render_template('admin_appointments.html', appointments=appointments)


# ---------------- Book Appointment ----------------
@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'user_id' not in session:
        flash("Please login to book an appointment.", "warning")
        return redirect(url_for('login'))

    doctors = Doctor.query.all()
    preselected_doctor_id = request.args.get('doctor_id', type=int)

    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date = request.form.get('date')
        time = request.form.get('time')

        if not doctor_id or not date or not time:
            flash("Please fill all fields.", "danger")
            return redirect(request.url)

        if Appointment.query.filter_by(doctor_id=doctor_id, date=date, time=time).first():
            flash("This time slot is already booked. Please choose another.", "danger")
            return redirect(request.url)

        appointment = Appointment(
            user_id=session['user_id'],
            doctor_id=doctor_id,
            date=date,
            time=time
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('appointments'))

    return render_template('book_appointment.html', doctors=doctors, preselected_doctor_id=preselected_doctor_id)


# ---------------- View Appointments ----------------
@app.route('/appointments')
def appointments():
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    user_appts = Appointment.query.filter_by(user_id=session['user_id']).all()
    return render_template('appointments.html', appointments=user_appts)


# ---------------- Edit Appointment ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_appointment(id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    appt = Appointment.query.get_or_404(id)

    if request.method == 'POST':
        appt.date = request.form['date']
        appt.time = request.form['time']
        db.session.commit()
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointments'))

    return render_template('edit_appointment.html', appt=appt)


# ---------------- Delete Appointment ----------------
@app.route('/delete/<int:id>')
def delete_appointment(id):
    if 'user_id' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    appt = Appointment.query.get_or_404(id)
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('appointments'))


# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)
