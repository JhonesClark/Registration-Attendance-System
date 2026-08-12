from ..extensions import db
from ..utils.time import now_ph


class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    action = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=now_ph)

    user = db.relationship('User', back_populates='activity_logs')
    person = db.relationship('Person', back_populates='activity_logs')

    def __repr__(self):
        return f"<ActivityLog {self.action} by {self.user_id} at {self.created_at}>"
