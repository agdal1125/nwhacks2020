"""Routes for user authentication."""
from flask import redirect, render_template, flash, Blueprint, request, url_for, session
from flask_login import login_required, logout_user, current_user, login_user
from flask import current_app as app
from werkzeug.security import generate_password_hash
from .assets import compile_auth_assets
from .forms import LoginForm, SignupForm
from .models import db, User
from . import login_manager
from datetime import datetime


# Blueprint Configuration
auth_pages = Blueprint('auth_pages', __name__,
                    template_folder='templates',
                    static_folder='static')
compile_auth_assets(app)

@auth_pages.route('/login', methods=['GET', 'POST'])
def login_page():
    """User login page."""
    # Bypass Login screen if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_pages.dashboard'))
    login_form = LoginForm(request.form)
    # POST: Create user and redirect them to the app
    if request.method == 'POST':
        if login_form.validate():
            # Get Form Fields
            email = request.form.get('email')
            password = request.form.get('password')
            # Validate Login Attempt
            user = User.query.filter_by(email=email).first()
            if user:
                if user.check_password(password=password):
                    login_user(user)
                    next = request.args.get('next')
                    # Save session
                    session["email"] = email
                    return redirect(next or url_for('main_pages.dashboard'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_pages.login_page'))
    # GET: Serve Log-in page
    return render_template('login.html',
                           form=LoginForm(),
                           title='Log in | Flask-Login Tutorial.',
                           template='login-page',
                           body="Log in with your User account.")


@auth_pages.route('/signup', methods=['GET', 'POST'])
def signup_page():

    """User sign-up page."""
    signup_form = SignupForm(request.form)

    # POST: Sign user in
    if request.method == 'POST':
        
        if signup_form.validate():
   
            # Get Form Fields
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            birthday = request.form.get('birthday')
            gender = request.form.get('gender')
            
            # Check if user exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user is None:
                print(type(birthday))
                type(birthday)
                user = User(name=name,
                            email=email,
                            password=generate_password_hash(password, method='sha256'),
                            birthday=birthday,
                            gender=gender)
              
                db.session.add(user)
                db.session.commit()

                # Save session
                session["email"] = email
                
                login_user(user)
                # Direct to setting profile
                return redirect(url_for('main_pages.profile_setting'))
                
            flash('A user already exists with that email address.')
            return redirect(url_for('auth_pages.signup_page'))
    # GET: Serve Sign-up page
    return render_template('/signup.html',
                           title='Create an Account | Youth Engage Senior',
                           form=SignupForm(),
                           template='signup-page',
                           body="Sign up for a user account.")


@auth_pages.route("/logout")
@login_required
def logout_page():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('auth_pages.login_page'))


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_pages.login_page'))
