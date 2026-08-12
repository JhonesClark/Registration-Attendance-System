from functools import wraps
from flask import abort
from flask_login import current_user

from .extensions import login_manager


def roles_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(f):
    return roles_required(['ADMIN'])(f)


def secretary_required(f):
    return roles_required(['SECRETARY'])(f)


def attendance_required(f):
    return roles_required(['ATTENDANCE'])(f)
