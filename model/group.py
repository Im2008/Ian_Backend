# group.py
from sqlite3 import IntegrityError
from __init__ import app, db

class Group(db.Model):
    """
    Group Model
    
    The Group class represents a specific community within a section.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the group.
        _name (db.Column): A string representing the name of the group.
        _section_id (db.Column): An integer representing the section to which the group belongs.
        _moderator_id (db.Column): An integer representing the user who is the moderator of the group.
    """
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=True, nullable=False)
    _section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    _moderator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    posts = db.relationship('Post', backref='group', lazy=True)

    def __init__(self, name, section_id, moderator_id=None):
        self._name = name
        self._section_id = section_id
        self._moderator_id = moderator_id
        
    @property
    def name(self):
        return self._name

    def __repr__(self):
        return f"Group(id={self.id}, name={self._name}, section_id={self._section_id}, moderator_id={self._moderator_id})"

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
    
    def read(self):
        return {
            'id': self.id,
            'name': self._name,
            'section_id': self._section_id,
            'moderator_id': self._moderator_id
        }
        
def initGroups():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        
        g1 = Group(name='Math Club', section_id=1, moderator_id=1)
        g2 = Group(name='Football Team', section_id=2, moderator_id=2)
        g3 = Group(name='Movie Buffs', section_id=3, moderator_id=3)
        
        groups = [g1, g2, g3]
        for group in groups:
            try:
                group.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {group.uid}")