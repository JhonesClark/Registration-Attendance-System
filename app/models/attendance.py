from ..extensions import db
from ..utils.time import now_ph


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    attendance_day_id = db.Column(db.Integer, db.ForeignKey('event_day.id'), nullable=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False, default=now_ph().date)
    attendance_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(32), nullable=False, default='Present')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=now_ph)

    person = db.relationship('Person', back_populates='attendance_records')
    user = db.relationship('User')
    event = db.relationship('Event', back_populates='attendance_records')
    attendance_day = db.relationship('EventDay', back_populates='attendance_records')

    __table_args__ = (
        db.UniqueConstraint('event_id', 'person_id', 'attendance_day_id', name='uq_event_day_person_attendance'),
    )

    def __repr__(self):
        return f"<Attendance {self.person_id} {self.attendance_date}>"
