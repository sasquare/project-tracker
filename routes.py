from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app
from database import db
from models import User, Project
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
@login_required
def index():
    try:
        projects = Project.query.all()
        project_data = [
            {
                "id": project.id,
                "name": project.name,
                "description": project.description or "No description",
                "status": project.status,
                "created_by_username": User.query.get(project.created_by).username
            }
            for project in projects
        ]
        return render_template('index.html', projects=project_data)
    except Exception as e:
        flash(f"Error loading projects: {str(e)}", "error")
        return render_template('index.html', projects=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        role = request.form.get('role', 'user').strip().lower()
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for('register'))
        if role not in ['user', 'admin']:
            flash("Role must be 'user' or 'admin'.", "error")
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for('register'))
        user = User(username=username, password=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for('login'))
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        flash("Invalid username or password.", "error")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form['description'].strip() or None
        if not name:
            flash("Project name is required.", "error")
            return redirect(url_for('new_project'))
        if len(name) > 100:
            flash("Project name must be 100 characters or less.", "error")
            return redirect(url_for('new_project'))
        project = Project(name=name, description=description, created_by=current_user.id)
        db.session.add(project)
        db.session.commit()
        flash("Project created successfully!", "success")
        return redirect(url_for('index'))
    return render_template('new_project.html')

@app.route('/project/<int:project_id>/update', methods=['POST'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    new_status = request.form['status']
    valid_statuses = ['initiated', 'approved', 'in_progress', 'completed', 'handed_over']
    
    if new_status not in valid_statuses:
        flash("Invalid status.", "error")
        return redirect(url_for('index'))
    
    if new_status == 'approved' and current_user.role != 'admin':
        flash("Only admins can approve projects.", "error")
        return redirect(url_for('index'))
    
    project.status = new_status
    db.session.commit()
    flash(f"Project status updated to {new_status}.", "success")
    return redirect(url_for('index'))