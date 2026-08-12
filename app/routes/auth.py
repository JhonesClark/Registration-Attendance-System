from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from ..extensions import login_manager
from ..forms import LoginForm
from ..models.user import User

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/')
def root_redirect():
    if current_user.is_authenticated:
        if current_user.role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        if current_user.role == 'ATTENDANCE':
            return redirect(url_for('attendance.dashboard'))
        return redirect(url_for('secretary.dashboard'))
    return redirect(url_for('auth.login'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        if current_user.role == 'ATTENDANCE':
            return redirect(url_for('attendance.dashboard'))
        return redirect(url_for('secretary.dashboard'))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        user = User.query.filter_by(username=username).first()

        if not user:
            form.username.errors.append('Invalid email')
            flash('Invalid email', 'danger')
            return render_template('auth/login.html', form=form, auth_error='email')

        if not check_password_hash(user.password_hash, password):
            form.password.errors.append('Invalid password')
            flash('Invalid password', 'danger')
            return render_template('auth/login.html', form=form, auth_error='password')

        login_user(user)
        session.permanent = True
        if user.role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        if user.role == 'ATTENDANCE':
            return redirect(url_for('attendance.dashboard'))
        return redirect(url_for('secretary.dashboard'))

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    if request.method == 'POST':
        return '', 204
    return redirect(url_for('auth.login'))
