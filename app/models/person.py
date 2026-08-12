from ..extensions import db
from ..utils.time import now_ph


class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(64), nullable=False)
    person_type = db.Column(db.String(64), nullable=False)
    registration_status = db.Column(db.String(64), nullable=False, default='Not Registered')
    registered_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=now_ph)
    updated_at = db.Column(db.DateTime, default=now_ph, onupdate=now_ph)
    updated_at = db.Column(db.DateTime, default=now_ph, onupdate=now_ph)

    activity_logs = db.relationship('ActivityLog', back_populates='person', lazy='dynamic')
    attendance_records = db.relationship('Attendance', back_populates='person', lazy='dynamic')

    def __repr__(self):
        return f"<Person {self.name}>"
