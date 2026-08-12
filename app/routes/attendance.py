from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func

from ..decorators import attendance_required, roles_required
from ..extensions import db, socketio
from ..models.activity_log import ActivityLog
from ..models.attendance import Attendance
from ..models.category import Category
from ..models.event import Event, EventDay
from ..models.person import Person
from ..utils.time import now_ph

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance', template_folder='../templates')


def get_active_event_day(event=None):
    event = event or Event.query.filter_by(status='Active').order_by(Event.created_at.desc()).first()
    if not event:
        return None, None
    day = EventDay.query.filter_by(event_id=event.id, id=event.active_day_id).first()
    if day is None:
        day = event.event_days.order_by(EventDay.day_number).first()
        if day:
            event.active_day_id = day.id
            db.session.commit()
    return event, day


def build_attendance_metrics():
    event, day = get_active_event_day()
    if not event or not day:
        registered_people = Person.query.filter_by(registration_status='Registered').all()
        return {'present': 0, 'absent': len(registered_people), 'categories': Category.query.order_by(Category.name).all(), 'event': None, 'day': None}
    registered_people = Person.query.filter_by(registration_status='Registered').all()
    present_count = Attendance.query.filter_by(event_id=event.id, attendance_day_id=day.id, status='Present').count()
    absent_count = max(0, len(registered_people) - present_count)
    categories = Category.query.order_by(Category.name).all()
    return {
        'present': present_count,
        'absent': absent_count,
        'categories': categories,
        'event': event,
        'day': day,
    }


@attendance_bp.route('/')
@login_required
@attendance_required
def dashboard():
    event, day = get_active_event_day()
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query = Person.query.filter_by(registration_status='Registered')
    if search:
        query = query.filter(func.lower(Person.name).contains(search.lower()))
    if category:
        query = query.filter_by(category=category)

    people = query.order_by(Person.name).all()
    attendance_by_person = {}
    if event and day:
        for record in Attendance.query.filter_by(event_id=event.id, attendance_day_id=day.id).all():
            attendance_by_person[record.person_id] = record
    metrics = build_attendance_metrics()

    return render_template(
        'attendance/dashboard.html',
        people=people,
        attendance_by_person=attendance_by_person,
        metrics=metrics,
        search=search,
        selected_category=category,
        event=event,
        day=day,
    )


@attendance_bp.route('/record/<int:person_id>', methods=['POST'])
@login_required
@attendance_required
def record_attendance(person_id):
    person = Person.query.get_or_404(person_id)
    if person.registration_status != 'Registered':
        flash('Only registered people can be marked present.', 'danger')
        return redirect(url_for('attendance.dashboard'))

    event, day = get_active_event_day()
    if not event or not day:
        flash('No active event or attendance day is available.', 'danger')
        return redirect(url_for('attendance.dashboard'))

    existing = Attendance.query.filter_by(event_id=event.id, attendance_day_id=day.id, person_id=person.id).first()
    if existing:
        flash(f'{person.name} is already marked Present for {event.name} Day {day.day_number}.', 'info')
        return redirect(url_for('attendance.dashboard'))

    now_time = now_ph().time()

    attendance = Attendance(
        event_id=event.id,
        attendance_day_id=day.id,
        person_id=person.id,
        attendance_date=day.date,
        attendance_time=now_time,
        status='Present',
        created_by=current_user.id,
    )
    db.session.add(attendance)

    activity = ActivityLog(
        user_id=current_user.id,
        person_id=person.id,
        action='Record attendance',
        description=f'{person.name} was marked Present for {event.name} Day {day.day_number} by {current_user.username}.',
    )
    db.session.add(activity)
    db.session.commit()

    payload = {
        'timestamp': activity.created_at.strftime('%I:%M %p'),
        'time': activity.created_at.strftime('%I:%M %p'),
        'date': activity.created_at.strftime('%B %d, %Y'),
        'user': current_user.username,
        'action': 'marked present',
        'name': person.name,
        'category': person.category,
        'person_type': person.person_type,
        'description': activity.description,
    }

    socketio.emit('attendance_update', payload)
    socketio.emit('new_activity', payload)
    socketio.emit('metrics_update', {
        'present': build_attendance_metrics()['present'],
        'absent': build_attendance_metrics()['absent'],
    })

    flash(f'{person.name} is now marked Present for {event.name} Day {day.day_number}.', 'success')
    return redirect(url_for('attendance.dashboard'))


@attendance_bp.route('/summary/json')
@login_required
@attendance_required
def attendance_summary_json():
    return jsonify(build_attendance_metrics())
