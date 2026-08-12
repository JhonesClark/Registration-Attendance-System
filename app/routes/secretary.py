from flask import Blueprint, render_template
from flask_login import login_required

from ..decorators import secretary_required
from ..models.person import Person

secretary_bp = Blueprint('secretary', __name__, url_prefix='/secretary', template_folder='../templates')


@secretary_bp.route('/')
@login_required
@secretary_required
def dashboard():
    total_people = Person.query.count()
    registered = Person.query.filter_by(registration_status='Registered').count()
    not_registered = Person.query.filter_by(registration_status='Not Registered').count()
    ladies = Person.query.filter_by(category='Ladies').count()
    men = Person.query.filter_by(category='Men').count()
    young_people = Person.query.filter_by(category='Young People').count()
    recent_registrations = Person.query.order_by(Person.created_at.desc()).limit(5).all()

    return render_template(
        'secretary/dashboard.html',
        total_people=total_people,
        registered=registered,
        not_registered=not_registered,
        ladies=ladies,
        men=men,
        young_people=young_people,
        recent_registrations=recent_registrations,
    )
