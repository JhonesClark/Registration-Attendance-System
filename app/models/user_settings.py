from ..extensions import db
from .user import User


class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    registration_notifications = db.Column(db.Boolean, default=True)
    activity_notifications = db.Column(db.Boolean, default=True)
    notification_sound = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(64), default='Asia/Manila')
    date_format = db.Column(db.String(64), default='MMMM D, YYYY')
    time_format = db.Column(db.String(8), default='12')

    user = db.relationship('User', back_populates='settings')

    def to_dict(self):
        return {
            'registration_notifications': bool(self.registration_notifications),
            'activity_notifications': bool(self.activity_notifications),
            'notification_sound': bool(self.notification_sound),
            'timezone': self.timezone,
            'date_format': self.date_format,
            'time_format': self.time_format,
        }
