from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, Users, Staff, Trek, Booking 
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# --- DECORATORS & CONTEXT PROCESSORS ----

# Protects routes so only logged-in users can access them
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

# Makes `current_user` available in all HTML templates automatically
@app.context_processor
def inject_user():
    current_user = None
    if 'user_id' in session:
        current_user = Users.query.get(session['user_id'])
    return dict(current_user=current_user)


# --- PUBLIC & AUTH ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Check if email exists
        if Users.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        new_user = Users(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.flush() # Get the new user's ID before committing

        # If they registered as staff, create their pending Staff profile
        if role == 'staff':
            contact = request.form.get('contact_number')
            experience = request.form.get('experience')
            new_staff = Staff(user_id=new_user.id, contact_number=contact, experience=experience)
            db.session.add(new_staff)

        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = Users.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if user.blacklisted:
                flash('Your account has been suspended.', 'error')
                return redirect(url_for('login'))

            # Log user in
            session['user_id'] = user.id
            session['role'] = user.role
            
            # Route to correct dashboard
            if user.role == 'admin': return redirect(url_for('admin_dashboard'))
            elif user.role == 'staff': return redirect(url_for('staff_dashboard'))
            else: return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))


# --- DASHBOARD ROUTES  ---

# --- ADMIN DASHBOARD ---

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    # Just grab some quick stats for the dashboard
    total_treks = Trek.query.count()
    total_users = Users.query.count()
    
    return render_template('admin/dashboard.html', total_treks=total_treks, total_users=total_users,)

# --- MANAGE TREKS (CRUD) ---

@app.route('/admin/manage_treks')
@login_required
def manage_treks():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    all_treks = Trek.query.all()
    # show_form=False means we just want to see the table
    return render_template('admin/manage_treks.html', treks=all_treks, show_form=False)

@app.route('/admin/manage_treks/create', methods=['GET', 'POST'])
@login_required
def create_trek():
    if session.get('role') != 'admin': return redirect(url_for('index'))

    if request.method == 'POST':
        new_trek = Trek(
            name=request.form.get('name'),
            location=request.form.get('location'),
            difficulty=request.form.get('difficulty'),
            duration=int(request.form.get('duration')),
            max_slots=int(request.form.get('max_slots')),
            available_slots=int(request.form.get('max_slots')),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date(),
            description=request.form.get('description'),
            status='Active'
        )
        db.session.add(new_trek)
        db.session.commit()
        flash('New Trek successfully created!', 'success')
        return redirect(url_for('manage_treks'))

    # show_form=True tells the HTML to render the input form instead of the table
    return render_template('admin/manage_treks.html', show_form=True, trek=None)

@app.route('/admin/manage_treks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_trek(id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    
    trek = Trek.query.get_or_404(id)

    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration = int(request.form.get('duration'))
        trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trek.description = request.form.get('description')
        trek.status = request.form.get('status')
        
        db.session.commit()
        flash('Trek updated successfully!', 'success')
        return redirect(url_for('manage_treks'))

    return render_template('admin/manage_treks.html', show_form=True, trek=trek)

@app.route('/admin/manage_treks/delete/<int:id>', methods=['POST'])
@login_required
def delete_trek(id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    
    trek = Trek.query.get_or_404(id)
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted completely.', 'success')
    return redirect(url_for('manage_treks'))


# --- MANAGE USERS ---

@app.route('/admin/manage_users')
@login_required
def manage_users():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    all_users = Users.query.all()
    return render_template('admin/manage_users.html', users=all_users, show_form=False)

@app.route('/admin/manage_users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    
    user = Users.query.get_or_404(id)

    if request.method == 'POST':
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        

        user.active = True if request.form.get('active') else False
        user.blacklisted = True if request.form.get('blacklisted') else False
        
        db.session.commit()
        flash('User profile updated!', 'success')
        return redirect(url_for('manage_users'))

    return render_template('admin/manage_users.html', show_form=True, user=user)


@app.route('/admin/manage_users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    user = Users.query.get_or_404(id)
    
    # Prevent deleting the main admin
    if user.email == 'admin@gmail.com':
        flash('Cannot delete the master admin account.', 'error')
        return redirect(url_for('manage_users'))
        
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('manage_users'))



# --- MANAGE STAFF ---

@app.route('/admin/manage_staff')
@login_required
def manage_staff():
    if session.get('role') != 'admin': return redirect(url_for('index'))
    
    all_staff = Staff.query.all()
    return render_template('admin/manage_staff.html', staff_list=all_staff)


@app.route('/admin/manage_staff/status/<int:id>/<status>')
@login_required
def update_staff_status(id, status):
    if session.get('role') != 'admin': return redirect(url_for('index'))
    
    staff_member = Staff.query.get_or_404(id)
    
    if status in ['approved', 'rejected', 'pending']:
        staff_member.approved_status = status
        db.session.commit()
        flash(f'Staff status updated to {status}.', 'success')
        
    return redirect(url_for('manage_staff'))


@app.route('/admin/assign_staff', methods=['GET', 'POST'])
@login_required
def assign_staff():
    if session.get('role') != 'admin': return redirect(url_for('index'))

    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        staff_user_id = request.form.get('staff_user_id')

        trek = Trek.query.get(trek_id)
        if trek:
            # If they select "Unassign" (empty string), set it to None
            trek.assigned_staff_id = staff_user_id if staff_user_id else None
            db.session.commit()
            flash(f'Staff assignment updated for "{trek.name}".', 'success')
            
        return redirect(url_for('assign_staff'))

    all_treks = Trek.query.all()
    approved_staff = Staff.query.filter_by(approved_status='approved').all()

    return render_template('admin/assign_staff.html', treks=all_treks, staff_list=approved_staff)


@app.route('/admin/search')
@login_required
def admin_search():
    if session.get('role') != 'admin':
        return redirect(url_for('index'))

    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('admin_dashboard'))

    # Search Treks (by name or location)
    search_term = f"%{query}%"
    found_treks = Trek.query.filter(
        (Trek.name.ilike(search_term)) | (Trek.location.ilike(search_term))
    ).all()

    # Search Users (by name or email)
    found_users = Users.query.filter(
        (Users.name.ilike(search_term)) | (Users.email.ilike(search_term))
    ).all()

    return render_template('admin/search_results.html', 
                           query=query, treks=found_treks, users=found_users)


# --- STAFF ROUTES ---

@app.route('/staff/dashboard')
@login_required
def staff_dashboard(): 
    if session.get('role') != 'staff':
        return redirect(url_for('index'))
    
    staff_profile = Staff.query.filter_by(user_id=session['user_id']).first()
    assigned_treks = Trek.query.filter_by(assigned_staff_id=session['user_id']).all()
    
    return render_template('staff/dashboard.html', 
                           staff_profile=staff_profile, 
                           assigned_treks=assigned_treks)

@app.route('/staff/manage_trek', methods=['GET', 'POST'])
@login_required
def staff_manage_trek():
    if session.get('role') != 'staff':
        return redirect(url_for('index'))

    # Security check
    staff_profile = Staff.query.filter_by(user_id=session['user_id']).first()
    if staff_profile.approved_status != 'approved':
        flash('Your account must be approved by an Admin to manage treks.', 'error')
        return redirect(url_for('staff_dashboard'))

    # POST: Update Trek Data (Status & Slots)
    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        trek = Trek.query.get(trek_id)
        
        # Security: Double-check they own this trek
        if trek and trek.assigned_staff_id == session['user_id']:
            trek.status = request.form.get('status')
            
            # Allow staff to manually adjust available slots
            new_slots = request.form.get('available_slots')
            if new_slots is not None:
                trek.available_slots = int(new_slots)
                
            db.session.commit()
            flash(f'{trek.name} has been successfully updated.', 'success')
            
        return redirect(url_for('staff_manage_trek'))

    # GET Request: Fetch their treks and all associated participants
    assigned_treks = Trek.query.filter_by(assigned_staff_id=session['user_id']).all()
    
    # Create a dictionary mapping trek_id to a list of its Bookings
    # This allows us to easily show participants for each specific trek in the HTML
    trek_bookings = {}
    for trek in assigned_treks:
        trek_bookings[trek.id] = Booking.query.filter_by(trek_id=trek.id).all()

    return render_template('staff/manage_trek.html', treks=assigned_treks, bookings=trek_bookings)



# --- USER ROUTES ---

@app.route('/user/dashboard')
@login_required
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('index'))
        
    # Dashboard shows their Active/Upcoming trips
    upcoming_bookings = Booking.query.join(Trek).filter(
        Booking.user_id == session['user_id'],
        Trek.status.in_(['Upcoming', 'Started', 'Active'])
    ).all()
    
    return render_template('user/dashboard.html', upcoming=upcoming_bookings)


@app.route('/user/browse_treks')
def browse_treks():
    search = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '')
    
    # show open treks
    query = Trek.query.filter(Trek.status.in_(['Upcoming', 'Active']))
    
    if search:
        search_term = f"%{search}%"
        query = query.filter((Trek.location.ilike(search_term)) | (Trek.name.ilike(search_term)))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
        
    treks = query.all()
    return render_template('user/browse_treks.html', treks=treks, search=search, difficulty=difficulty)


@app.route('/book/<int:trek_id>', methods=['POST'])
@login_required
def book_trek(trek_id):
    if session.get('role') != 'user':
        flash('Only trekkers can book expeditions.', 'error')
        return redirect(url_for('browse_treks'))
        
    trek = Trek.query.get_or_404(trek_id)
    
    # Validation Rules
    if trek.status not in ['Upcoming', 'Active']:
        flash('This trek is closed.', 'error')
    elif trek.available_slots <= 0:
        flash('This expedition is fully booked.', 'error')
    elif Booking.query.filter_by(user_id=session['user_id'], trek_id=trek_id).first():
        flash('You have already booked this expedition!', 'warning')
    else:
        # Success
        new_booking = Booking(user_id=session['user_id'], trek_id=trek_id)
        trek.available_slots -= 1 
        db.session.add(new_booking)
        db.session.commit()
        flash(f'Successfully booked {trek.name}!', 'success')
        
    return redirect(url_for('user_dashboard'))


@app.route('/user/history')
@login_required
def booking_history():
    if session.get('role') != 'user':
        return redirect(url_for('index'))
        
    # History shows ALL past and present bookings
    all_bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/booking_history.html', bookings=all_bookings)

# Profile Management for Users
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    if session.get('role') != 'user':
        return redirect(url_for('index'))
        
    # Fetch the current user from the database
    user = Users.query.get(session['user_id'])
    
    if request.method == 'POST':
        new_name = request.form.get('name').strip()
        new_email = request.form.get('email').strip()
        new_password = request.form.get('new_password').strip()
        
        # Check if they are trying to change their email to one that already exists
        if new_email != user.email:
            existing_user = Users.query.filter_by(email=new_email).first()
            if existing_user:
                flash('That email address is already in use by another account.', 'error')
                return redirect(url_for('user_profile'))
            user.email = new_email
            
        #  Update name
        user.name = new_name
        session['name'] = new_name  # Update their name in the current browser session too!
        
        #  Update password (only if they typed a new one)
        if new_password:
            user.password = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Your profile has been successfully updated.', 'success')
        return redirect(url_for('user_dashboard'))
        
    return render_template('user/profile.html', user=user)


# --- INITIALIZATION ---
def create_admin():
    admin = Users.query.filter_by(email='admin@gmail.com').first()
    if not admin:
        admin = Users(
            name='Admin',
            email='admin@gmail.com',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print(" Admin account created (admin@gmail.com / admin123)")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True)