from ..utils.time import now_ph

from flask_login import UserMixin

from ..extensions import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=now_ph)

    activity_logs = db.relationship('ActivityLog', back_populates='user', lazy='dynamic')
    settings = db.relationship('UserSettings', back_populates='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"
