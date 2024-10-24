# section.py
from __init__ import app, db

class Section(db.Model):
    """
    Section Model
    
    The Section class represents a broad area of interest.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the section.
        _name (db.Column): A string representing the name of the section.
        _theme (db.Column): A string representing the theme of the section.
    """
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=True, nullable=False)
    _theme = db.Column(db.String(255), nullable=True)

    groups = db.relationship('Group', backref='section', lazy=True)

    def __init__(self, name, theme=None):
        self._name = name
        self._theme = theme

    def __repr__(self):
        return f"Section(id={self.id}, name={self._name}, theme={self._theme})"

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

def initSections():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""