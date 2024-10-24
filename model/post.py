# post.py
from sqlalchemy import Text
from __init__ import app, db

class Post(db.Model):
    """
    Post Model
    
    The Post class represents an individual contribution or discussion within a group.
    
    Attributes:
        id (db.Column): The primary key, an integer representing the unique identifier for the post.
        _title (db.Column): A string representing the title of the post.
        _content (db.Column): A Text blob representing the content of the post.
        _user_id (db.Column): An integer representing the user who created the post.
        _group_id (db.Column): An integer representing the group to which the post belongs.
    """
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(255), nullable=False)
    _content = db.Column(Text, nullable=False)
    _user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    _group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

    def __init__(self, title, content, user_id, group_id):
        self._title = title
        self._content = content
        self._user_id = user_id
        self._group_id = group_id

    def __repr__(self):
        return f"Post(id={self.id}, title={self._title}, content={self._content}, user_id={self._user_id}, group_id={self._group_id})"

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
def initPosts():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""