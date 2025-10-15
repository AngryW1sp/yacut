from .yacut import db
from sqlalchemy.sql import func


class URLMap(db.Model):
    __tablename__ = "url_map"

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(16), unique=True,
                      nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, default=func.now(), nullable=False, index=True)