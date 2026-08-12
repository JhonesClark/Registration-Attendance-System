from ..extensions import db
from ..utils.time import now_ph


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=now_ph)
    updated_at = db.Column(db.DateTime, default=now_ph, onupdate=now_ph)

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_active': bool(self.is_active),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
