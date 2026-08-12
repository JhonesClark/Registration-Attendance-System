import os
from pathlib import Path
from datetime import datetime, timedelta
from .utils.time import now_ph

from dotenv import load_dotenv
from flask import Flask, request
from flask_wtf import CSRFProtect
from werkzeug.security import generate_password_hash

from .extensions import db, login_manager, socketio
from .errors import register_error_handlers
from .models.user import User
from .models.category import Category
from .models.event import Event, EventDay


def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    database_url = os.getenv('DATABASE_URL', '').strip()
    if database_url.startswith('sqlite:///'):
        sqlite_path = database_url[len('sqlite:///'):]
        if sqlite_path and not Path(sqlite_path).is_absolute():
            sqlite_path = (Path.cwd() / sqlite_path).resolve()
            database_url = f'sqlite:///{sqlite_path.as_posix()}'
    elif not database_url:
        database_path = instance_path / 'home_builders.db'
        database_url = f'sqlite:///{database_path.as_posix()}'

    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY') or os.urandom(24),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)
    login_manager.init_app(app)
    CSRFProtect(app)
    socketio.init_app(app, cors_allowed_origins='*', async_mode='threading')
    login_manager.login_view = 'auth.login'

    @app.after_request
    def add_auth_headers(response):
        # Authentication and protected pages must never be cacheable in the browser
        # after a user has signed in, because a stale /login response can otherwise
        # appear when the user presses the Back button.
        auth_endpoints = {
            'auth.login', 'admin.dashboard', 'admin.export_page', 'admin.import_page', 'admin.activity',
            'secretary.dashboard', 'people.list_people', 'people.add_person', 'people.view_person',
            'people.edit_person', 'people.delete_person', 'people.register_person', 'attendance.dashboard',
            'attendance.record_attendance', 'admin.categories', 'admin.add_category', 'admin.edit_category',
            'admin.toggle_category', 'admin.attendance', 'admin.attendance_data', 'admin.attendance_export',
            'admin.update_attendance_status', 'admin.clear_attendance_filters'
        }
        if request.endpoint in auth_endpoints or current_user_is_authenticated(request):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Vary'] = 'Cookie, Authorization'
        else:
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    register_error_handlers(app)

    # register blueprints (placeholders)
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.secretary import secretary_bp
    from .routes.people import people_bp
    from .routes.export_import import ei_bp
    from .routes.profile import profile_bp
    from .routes.attendance import attendance_bp
    # ensure models import so tables are created
    from .models import UserSettings

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(secretary_bp)
    app.register_blueprint(people_bp)
    app.register_blueprint(ei_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(attendance_bp)

    init_database(app)

    return app


def init_database(app):
    with app.app_context():
        db.create_all()
        run_station_cleanup_migration(app)
        ensure_event_schema_migration(app)
        create_default_categories()
        create_default_users()
        ensure_default_event()


def create_default_categories():
    default_categories = [
        'Ladies',
        'Men',
        'Young People',
        'Young Professionals',
    ]
    for name in default_categories:
        existing = Category.query.filter_by(name=name).first()
        if not existing:
            new_category = Category(name=name)
            db.session.add(new_category)
    db.session.commit()


def run_station_cleanup_migration(app):
    if not app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
        return

    with db.engine.begin() as connection:
        try:
            columns = [row[1] for row in connection.exec_driver_sql('PRAGMA table_info(person)').fetchall()]
        except Exception:
            return

        if 'registration_station' not in columns:
            return

        connection.exec_driver_sql('''
            CREATE TABLE person_station_migration (
                id INTEGER PRIMARY KEY,
                name VARCHAR(256) NOT NULL,
                category VARCHAR(64) NOT NULL,
                person_type VARCHAR(64) NOT NULL,
                registration_status VARCHAR(64) NOT NULL,
                registered_at DATETIME,
                created_at DATETIME,
                updated_at DATETIME
            )
        ''')
        connection.exec_driver_sql('''
            INSERT INTO person_station_migration (
                id,
                name,
                category,
                person_type,
                registration_status,
                registered_at,
                created_at,
                updated_at
            )
            SELECT
                id,
                name,
                category,
                person_type,
                registration_status,
                registered_at,
                created_at,
                updated_at
            FROM person
        ''')
        connection.exec_driver_sql('DROP TABLE person')
        connection.exec_driver_sql('ALTER TABLE person_station_migration RENAME TO person')


def current_user_is_authenticated(request_obj):
    # The request context may not have a user object in some before/after hooks,
    # so we resolve the authenticated identity from flask-login only when possible.
    try:
        from flask_login import current_user
        return current_user.is_authenticated
    except Exception:
        return False


def ensure_event_schema_migration(app):
    if not app.config.get('SQLALCHEMY_DATABASE_URI', '').startswith('sqlite'):
        return

    with db.engine.begin() as connection:
        try:
            attendance_columns = [row[1] for row in connection.exec_driver_sql('PRAGMA table_info(attendance)').fetchall()]
        except Exception:
            attendance_columns = []

        if 'event_id' not in attendance_columns:
            connection.exec_driver_sql('ALTER TABLE attendance ADD COLUMN event_id INTEGER')
            connection.exec_driver_sql('ALTER TABLE attendance ADD COLUMN attendance_day_id INTEGER')

        if 'punctuality' in attendance_columns:
            legacy_exists = connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance_legacy'").fetchone()
            if legacy_exists is None:
                connection.exec_driver_sql('ALTER TABLE attendance RENAME TO attendance_legacy')
                connection.exec_driver_sql('''
                    CREATE TABLE attendance (
                        id INTEGER PRIMARY KEY,
                        event_id INTEGER,
                        attendance_day_id INTEGER,
                        person_id INTEGER NOT NULL,
                        attendance_date DATE NOT NULL,
                        attendance_time TIME NOT NULL,
                        status VARCHAR(32) NOT NULL DEFAULT 'Present',
                        created_by INTEGER NOT NULL,
                        created_at DATETIME,
                        FOREIGN KEY(event_id) REFERENCES event(id),
                        FOREIGN KEY(attendance_day_id) REFERENCES event_day(id),
                        FOREIGN KEY(person_id) REFERENCES person(id),
                        FOREIGN KEY(created_by) REFERENCES user(id)
                    )
                ''')
                connection.exec_driver_sql('''
                    INSERT INTO attendance (
                        id, event_id, attendance_day_id, person_id, attendance_date, attendance_time, status, created_by, created_at
                    )
                    SELECT
                        id, event_id, attendance_day_id, person_id, attendance_date, attendance_time, status, created_by, created_at
                    FROM attendance_legacy
                ''')
                connection.exec_driver_sql('DROP TABLE attendance_legacy')

        try:
            connection.exec_driver_sql('PRAGMA table_info(event)').fetchall()
        except Exception:
            connection.exec_driver_sql('''
                CREATE TABLE event (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200) NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    status VARCHAR(32) NOT NULL,
                    active_day_id INTEGER,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            ''')

        try:
            connection.exec_driver_sql('PRAGMA table_info(event_day)').fetchall()
        except Exception:
            connection.exec_driver_sql('''
                CREATE TABLE event_day (
                    id INTEGER PRIMARY KEY,
                    event_id INTEGER NOT NULL,
                    day_number INTEGER NOT NULL,
                    date DATE NOT NULL,
                    is_active BOOLEAN NOT NULL,
                    created_at DATETIME,
                    FOREIGN KEY(event_id) REFERENCES event(id)
                )
            ''')

        try:
            connection.exec_driver_sql('CREATE UNIQUE INDEX uq_event_day_number ON event_day(event_id, day_number)')
        except Exception:
            pass
        try:
            connection.exec_driver_sql('CREATE UNIQUE INDEX uq_event_day_date ON event_day(event_id, date)')
        except Exception:
            pass
        try:
            connection.exec_driver_sql('CREATE UNIQUE INDEX uq_event_day_person_attendance ON attendance(event_id, person_id, attendance_day_id)')
        except Exception:
            pass


def ensure_default_event():
    if Event.query.first():
        event = Event.query.order_by(Event.created_at.asc()).first()
        if event and not event.active_day_id:
            first_day = event.event_days.order_by(EventDay.day_number).first()
            if first_day:
                event.active_day_id = first_day.id
        db.session.commit()
        return

    start_date = now_ph().date()
    end_date = start_date + timedelta(days=2)
    event = Event(
        name='Home Builders 2026',
        start_date=start_date,
        end_date=end_date,
        status='Active',
    )
    db.session.add(event)
    db.session.flush()

    for index in range(1, 4):
        event_day = EventDay(
            event_id=event.id,
            day_number=index,
            date=start_date + timedelta(days=index - 1),
            is_active=(index == 1),
        )
        db.session.add(event_day)
    db.session.flush()

    first_day = EventDay.query.filter_by(event_id=event.id).order_by(EventDay.day_number).first()
    if first_day:
        event.active_day_id = first_day.id
    event.status = 'Active'
    db.session.commit()


def create_default_users():
    default_accounts = [
        {'username': 'BCMBC', 'role': 'ADMIN', 'password': '12345'},
        {'username': 'bcmbc', 'role': 'SECRETARY', 'password': '12345'},
        {'username': 'BcmBc', 'role': 'ATTENDANCE', 'password': '12345'},
    ]

    for account in default_accounts:
        user = User.query.filter_by(username=account['username']).first()
        if not user:
            user = User(
                username=account['username'],
                password_hash=generate_password_hash(account['password']),
                role=account['role'],
                created_at=now_ph(),
            )
            db.session.add(user)

    db.session.commit()
