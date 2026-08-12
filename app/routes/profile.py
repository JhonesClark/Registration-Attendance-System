from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from ..forms import ChangeEmailForm, ChangePasswordForm
from ..extensions import db
from ..models.user import User
from ..models.user_settings import UserSettings
from flask import jsonify
from ..models.activity_log import ActivityLog
from datetime import datetime

profile_bp = Blueprint('profile', __name__, template_folder='../templates')


@profile_bp.route('/profile')
@login_required
def view_profile():
    return render_template('profile.html')


@profile_bp.route('/settings')
@login_required
def settings():
    # ensure the current user has a settings record
    if not current_user.settings:
        s = UserSettings(user_id=current_user.id)
        db.session.add(s)
        db.session.commit()
    # try to determine last successful login from activity logs (if any)
    last_login = None
    try:
        last = ActivityLog.query.filter(ActivityLog.user_id == current_user.id, ActivityLog.action.ilike('%login%')).order_by(ActivityLog.created_at.desc()).first()
        if last:
            last_login = last.created_at
    except Exception:
        last_login = None

    return render_template('settings.html', last_login=last_login)


@profile_bp.route('/settings/json')
@login_required
def settings_json():
    if not current_user.settings:
        s = UserSettings(user_id=current_user.id)
        db.session.add(s)
        db.session.commit()
    return jsonify(current_user.settings.to_dict())


@profile_bp.route('/settings/update', methods=['POST'])
@login_required
def settings_update():
    data = request.get_json() or {}
    if not current_user.settings:
        s = UserSettings(user_id=current_user.id)
        db.session.add(s)
    else:
        s = current_user.settings

    # only allow known keys
    for key in ('registration_notifications', 'activity_notifications', 'notification_sound', 'timezone', 'date_format', 'time_format'):
        if key in data:
            setattr(s, key, data[key])

    db.session.commit()
    return jsonify({'status': 'ok', 'settings': s.to_dict()})


@profile_bp.route('/profile/change-email', methods=['POST'])
@login_required
def change_email():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_email = form.new_email.data.strip()

        # verify password
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile.view_profile'))

        # check uniqueness
        existing = User.query.filter_by(username=new_email).first()
        if existing and existing.id != current_user.id:
            flash('The provided email/username is already in use.', 'danger')
            return redirect(url_for('profile.view_profile'))

        current_user.username = new_email
        db.session.commit()
        flash('Email updated successfully.', 'success')
        return redirect(url_for('profile.view_profile'))

    flash('Invalid input for changing email.', 'danger')
    return redirect(url_for('profile.view_profile'))


@profile_bp.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data

        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('profile.view_profile'))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Password changed successfully.', 'success')
        return redirect(url_for('profile.view_profile'))

    flash('Invalid input for changing password.', 'danger')
    return redirect(url_for('profile.view_profile'))



@profile_bp.route('/profile/change-email-json', methods=['POST'])
@login_required
def change_email_json():
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_email = (data.get('new_email') or '').strip()
    confirm_email = (data.get('confirm_email') or '').strip()

    if not current_password or not new_email or not confirm_email:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

    if new_email != confirm_email:
        return jsonify({'status': 'error', 'message': 'Emails must match.'}), 400

    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect.'}), 403

    existing = User.query.filter_by(username=new_email).first()
    if existing and existing.id != current_user.id:
        return jsonify({'status': 'error', 'message': 'The provided email/username is already in use.'}), 400

    current_user.username = new_email
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Email updated successfully.', 'username': current_user.username})


@profile_bp.route('/profile/change-password-json', methods=['POST'])
@login_required
def change_password_json():
    data = request.get_json() or {}
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    confirm_password = data.get('confirm_password', '')

    if not current_password or not new_password or not confirm_password:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

    if new_password != confirm_password:
        return jsonify({'status': 'error', 'message': 'Passwords must match.'}), 400

    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'status': 'error', 'message': 'Current password is incorrect.'}), 403

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'status': 'ok', 'message': 'Password changed successfully.'})
