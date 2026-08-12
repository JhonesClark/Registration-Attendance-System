from ..utils.time import now_ph

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from ..decorators import admin_required, roles_required
from ..forms import PersonForm
from ..models.activity_log import ActivityLog
from ..models.person import Person
from ..extensions import db, socketio

people_bp = Blueprint('people', __name__, url_prefix='/people', template_folder='../templates')


def build_metrics_payload():
    total_people = Person.query.count()
    registered = Person.query.filter_by(registration_status='Registered').count()
    not_registered = Person.query.filter_by(registration_status='Not Registered').count()
    ladies = Person.query.filter_by(category='Ladies').count()
    men = Person.query.filter_by(category='Men').count()
    young_people = Person.query.filter_by(category='Young People').count()
    members = Person.query.filter_by(person_type='Member').count()
    visitors = Person.query.filter_by(person_type='Visitor').count()
    return {
        'total_people': total_people,
        'registered': registered,
        'not_registered': not_registered,
        'ladies': ladies,
        'men': men,
        'young_people': young_people,
        'members': members,
        'visitors': visitors,
        'progress_pct': int((registered / total_people) * 100) if total_people else 0,
    }


def emit_admin_updates(event_name, payload):
    # `broadcast=True` is forwarded through Flask-SocketIO into the low-level
    # python-socketio server API that does not accept that keyword in this
    # environment. A plain emit() sends to all connected clients by default.
    socketio.emit(event_name, payload)


@people_bp.route('/')
@login_required
@roles_required(['ADMIN', 'SECRETARY'])
def list_people():
    query = Person.query
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    person_type = request.args.get('person_type', '').strip()
    registration_status = request.args.get('registration_status', '').strip()

    if search:
        query = query.filter(func.lower(Person.name).contains(search.lower()))
    if category:
        query = query.filter_by(category=category)
    if person_type:
        query = query.filter_by(person_type=person_type)
    if registration_status:
        query = query.filter_by(registration_status=registration_status)

    people = query.order_by(Person.created_at.desc()).all()
    categories = ['Ladies', 'Men', 'Young People']
    return render_template(
        'people/list.html',
        people=people,
        categories=categories,
        search=search,
        selected_category=category,
        selected_person_type=person_type,
        selected_registration_status=registration_status,
    )


@people_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required(['ADMIN', 'SECRETARY'])
def add_person():
    form = PersonForm()
    duplicates = []
    duplicate_warning = False

    if form.validate_on_submit():
        name_value = ' '.join(form.name.data.split()).strip()
        normalized_name = name_value.lower()
        duplicates = Person.query.filter(func.lower(func.trim(Person.name)) == normalized_name).all()

        if duplicates:
            duplicate_warning = True
            return render_template(
                'people/add.html',
                form=form,
                duplicates=duplicates,
                duplicate_warning=duplicate_warning,
                name_value=name_value,
            )

        person = Person(
            name=name_value,
            category=form.category.data,
            person_type=form.person_type.data,
            registration_status='Not Registered',
        )
        db.session.add(person)
        db.session.flush()

        activity = ActivityLog(
            user_id=current_user.id,
            person_id=person.id,
            action='Add person',
            description=f'{person.name} was added',
        )
        db.session.add(activity)
        db.session.commit()

        emit_admin_updates('new_activity', {
            'timestamp': activity.created_at.strftime('%I:%M %p'),
            'time': activity.created_at.strftime('%I:%M %p'),
            'date': activity.created_at.strftime('%B %d, %Y'),
            'user': current_user.username,
            'action': 'added',
            'name': person.name,
            'category': person.category,
            'person_type': person.person_type,
            'description': activity.description,
        })
        emit_admin_updates('metrics_update', build_metrics_payload())

        flash('Person added successfully.', 'success')
        return redirect(url_for('people.list_people'))

    return render_template('people/add.html', form=form, duplicates=duplicates, duplicate_warning=duplicate_warning)


@people_bp.route('/<int:id>')
@login_required
@roles_required(['ADMIN', 'SECRETARY'])
def view_person(id):
    person = Person.query.get_or_404(id)
    return render_template('people/view.html', person=person)


@people_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required(['ADMIN', 'SECRETARY'])
def edit_person(id):
    person = Person.query.get_or_404(id)
    form = PersonForm(obj=person)

    if form.validate_on_submit():
        person.name = ' '.join(form.name.data.split()).strip()
        person.category = form.category.data
        person.person_type = form.person_type.data
        db.session.add(person)

        activity = ActivityLog(
            user_id=current_user.id,
            person_id=person.id,
            action='Edit person',
            description=f'{person.name} was edited',
        )
        db.session.add(activity)
        db.session.commit()

        emit_admin_updates('new_activity', {
            'timestamp': activity.created_at.strftime('%I:%M %p'),
            'time': activity.created_at.strftime('%I:%M %p'),
            'date': activity.created_at.strftime('%B %d, %Y'),
            'user': current_user.username,
            'action': 'edited',
            'name': person.name,
            'category': person.category,
            'person_type': person.person_type,
            'description': activity.description,
        })

        flash('Person updated successfully.', 'success')
        return redirect(url_for('people.view_person', id=id))

    return render_template('people/edit.html', form=form, person=person)


@people_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_person(id):
    person = Person.query.get_or_404(id)
    activity = ActivityLog(
        user_id=current_user.id,
        person_id=person.id,
        action='Delete person',
        description=f'{person.name} was deleted',
    )
    db.session.add(activity)
    db.session.delete(person)
    db.session.commit()

    emit_admin_updates('new_activity', {
        'timestamp': activity.created_at.strftime('%I:%M %p'),
        'time': activity.created_at.strftime('%I:%M %p'),
        'date': activity.created_at.strftime('%B %d, %Y'),
        'user': current_user.username,
        'action': 'deleted',
        'name': person.name,
        'category': person.category,
        'person_type': person.person_type,
        'description': activity.description,
    })
    emit_admin_updates('metrics_update', build_metrics_payload())

    flash('Person deleted successfully.', 'success')
    return redirect(url_for('people.list_people'))


@people_bp.route('/<int:id>/register', methods=['POST'])
@login_required
@roles_required(['ADMIN', 'SECRETARY'])
def register_person(id):
    person = Person.query.get_or_404(id)
    if person.registration_status == 'Registered':
        flash('Person is already registered.', 'info')
        return redirect(url_for('people.view_person', id=id))

    person.registration_status = 'Registered'
    person.registered_at = now_ph()
    db.session.add(person)

    activity = ActivityLog(
        user_id=current_user.id,
        person_id=person.id,
        action='Register person',
        description=f'{person.name} was registered' + (f' by {current_user.username}' if current_user.role == 'SECRETARY' else ''),
    )
    db.session.add(activity)
    db.session.commit()

    emit_admin_updates('new_registration', {
        'timestamp': activity.created_at.strftime('%I:%M %p'),
        'id': person.id,
        'time': activity.created_at.strftime('%I:%M %p'),
        'date': activity.created_at.strftime('%B %d, %Y'),
        'name': person.name,
        'category': person.category,
        'person_type': person.person_type,
        'description': activity.description,
    })
    emit_admin_updates('new_activity', {
        'timestamp': activity.created_at.strftime('%I:%M %p'),
        'time': activity.created_at.strftime('%I:%M %p'),
        'date': activity.created_at.strftime('%B %d, %Y'),
        'user': current_user.username,
        'action': 'registered',
        'name': person.name,
        'category': person.category,
        'person_type': person.person_type,
        'description': activity.description,
    })
    emit_admin_updates('metrics_update', build_metrics_payload())
    flash('Registration Successful.', 'success')
    return redirect(url_for('people.view_person', id=id))
