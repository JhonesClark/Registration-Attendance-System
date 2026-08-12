from ..extensions import db
from ..utils.time import now_ph


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(32), nullable=False, default='Upcoming')
    active_day_id = db.Column(db.Integer, db.ForeignKey('event_day.id'))
    created_at = db.Column(db.DateTime, default=now_ph)
    updated_at = db.Column(db.DateTime, default=now_ph, onupdate=now_ph)

    event_days = db.relationship(
        'EventDay',
        back_populates='event',
        cascade='all, delete-orphan',
        lazy='dynamic',
        foreign_keys='EventDay.event_id',
    )
    attendance_records = db.relationship('Attendance', back_populates='event', lazy='dynamic')
    active_day = db.relationship('EventDay', foreign_keys=[active_day_id], post_update=True)

    def __repr__(self):
        return f'<Event {self.name}>'


class EventDay(db.Model):
    __tablename__ = 'event_day'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=now_ph)

    event = db.relationship('Event', back_populates='event_days', foreign_keys=[event_id])
    attendance_records = db.relationship('Attendance', back_populates='attendance_day', lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('event_id', 'day_number', name='uq_event_day_number'),
        db.UniqueConstraint('event_id', 'date', name='uq_event_day_date'),
    )

    def __repr__(self):
        return f'<EventDay {self.event_id} - Day {self.day_number}>'
