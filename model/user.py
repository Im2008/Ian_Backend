""" database dependencies to support sqliteDB examples """
from flask import current_app
from flask_login import UserMixin
from datetime import date
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

from __init__ import app, db

""" Helper Functions """

def default_year():
    """Returns the default year for user enrollment based on the current month."""
    current_month = date.today().month
    current_year = date.today().year
    # If current month is between August (8) and December (12), the enrollment year is next year.
    if 7 <= current_month <= 12:
        current_year = current_year + 1
    return current_year 

""" Database Models """

''' Tutorial: https://www.sqlalchemy.org/library.html#tutorials, try to get into Python shell and follow along '''

class User(db.Model, UserMixin):
    """
    User Model

    This class represents the User model, which is used to manage actions in the 'users' table of the database. It is an
    implementation of Object Relational Mapping (ORM) using SQLAlchemy, allowing for easy interaction with the database
    using Python code. The User model includes various fields and methods to support user management, authentication,
    and profile management functionalities.

    Attributes:
        __tablename__ (str): Specifies the name of the table in the database.
        id (Column): The primary key, an integer representing the unique identifier for the user.
        _name (Column): A string representing the user's name. It is not unique and cannot be null.
        _uid (Column): A unique string identifier for the user, cannot be null.
        _password (Column): A string representing the hashed password of the user. It is not unique and cannot be null.
        _role (Column): A string representing the user's role within the application. Defaults to "User".
        _pfp (Column): A string representing the path to the user's profile picture. It can be null.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(255), unique=False, nullable=False)
    _uid = db.Column(db.String(255), unique=True, nullable=False)
    _email = db.Column(db.String(255), unique=False, nullable=False)
    _password = db.Column(db.String(255), unique=False, nullable=False)
    _role = db.Column(db.String(20), default="User", nullable=False)
    _pfp = db.Column(db.String(255), unique=False, nullable=True)
   
    # Define many-to-many relationship with Section model through UserSection table 
    # Overlaps setting avoids cicular dependencies with UserSection class
    posts = db.relationship('Post', backref='author', lazy=True)
    moderated_groups = db.relationship('Group', backref='moderator', lazy=True)                              
    
    def __init__(self, name, uid, password=app.config["DEFAULT_PASSWORD"], role="User", pfp=''):
        self._name = name
        self._uid = uid
        self._email = "?"
        self.set_password(password)
        self._role = role
        self._pfp = pfp

    # UserMixin/Flask-Login requires a get_id method to return the id as a string
    def get_id(self):
        return str(self.id)

    # UserMixin/Flask-Login requires is_authenticated to be defined
    @property
    def is_authenticated(self):
        return True

    # UserMixin/Flask-Login requires is_active to be defined
    @property
    def is_active(self):
        return True

    # UserMixin/Flask-Login requires is_anonymous to be defined
    @property
    def is_anonymous(self):
        return False
    
    # validate uid is a unique GitHub username
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, email):
        if email is None or email == "":
            self._email = "?"
        else:
            self._email = email
        
    def set_email(self):
        """Set the email of the user based on the UID, the GitHub username."""
        data, status = GitHubUser().get(self._uid)
        if status == 200:
            self.email = data.get("email", "?")
            pass
        else:
            self.email = "?"

    # a name getter method, extracts name from object
    @property
    def name(self):
        return self._name

    # a setter function, allows name to be updated after initial object creation
    @name.setter
    def name(self, name):
        self._name = name

    # a getter method, extracts email from object
    @property
    def uid(self):
        return self._uid

    # a setter function, allows name to be updated after initial object creation
    @uid.setter
    def uid(self, uid):
        self._uid = uid

    # check if uid parameter matches user id in object, return boolean
    def is_uid(self, uid):
        return self._uid == uid

    @property
    def password(self):
        return self._password[0:10] + "..."  # because of security only show 1st characters

            
    # set password, this is conventional setter with business logic
    def set_password(self, password):
        """Create a hashed password."""
        self._password = generate_password_hash(password, "pbkdf2:sha256", salt_length=10)

    # check password parameter versus stored/encrypted password
    def is_password(self, password):
        """Check against hashed password."""
        result = check_password_hash(self._password, password)
        return result

    # output content using str(object) in human readable form, uses getter
    # output content using json dumps, this is ready for API response
    def __str__(self):
        return json.dumps(self.read())

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, role):
        self._role = role

    def is_admin(self):
        return self._role == "Admin"
    
    # getter method for profile picture
    @property
    def pfp(self):
        return self._pfp

    # setter function for profile picture
    @pfp.setter
    def pfp(self, pfp):
        self._pfp = pfp

    # CRUD create/add a new record to the table
    # returns self or None on error
    def create(self, inputs=None):
        try:
            db.session.add(self)  # add prepares to persist person object to Users table
            db.session.commit()  # SqlAlchemy "unit of work pattern" requires a manual commit
            if inputs:
                self.update(inputs)
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    # CRUD read converts self to dictionary
    # returns dictionary
    def read(self):
        data = {
            "id": self.id,
            "uid": self.uid,
            "name": self.name,
            "email": self.email,
            "role": self._role,
            "pfp": self._pfp,
        }
        return data
        
    # CRUD update: updates user name, password, phone
    # returns self
    def update(self, inputs):
        if not isinstance(inputs, dict):
            return self

        name = inputs.get("name", "")
        uid = inputs.get("uid", "")
        password = inputs.get("password", "")
        pfp = inputs.get("pfp", None)

        # Update table with new data
        if name:
            self.name = name
        if uid:
            self.set_uid(uid)
        if password:
            self.set_password(password)
        if pfp is not None:
            self.pfp = pfp

        # Check this on each update
        self.set_email()

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return None
        return self
    
    # CRUD delete: remove self
    # None
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
        return None   
    
    def save_pfp(self, image_data, filename):
        """For saving profile picture."""
        try:
            user_dir = os.path.join(app.config['UPLOAD_FOLDER'], self.uid)
            if not os.path.exists(user_dir):
                os.makedirs(user_dir)
            file_path = os.path.join(user_dir, filename)
            with open(file_path, 'wb') as img_file:
                img_file.write(image_data)
            self.update({"pfp": filename})
        except Exception as e:
            raise e
        
    def delete_pfp(self):
        """Deletes profile picture from user record."""
        self.pfp = None
        db.session.commit()
        
    def set_uid(self, new_uid=None):
        """
        Update the user's directory based on the new UID provided.

        :param new_uid: Optional new UID to update the user's directory.
        :return: The updated user object.
        """
        # Store the old UID for later comparison
        old_uid = self._uid
        # Update the UID if a new one is provided
        if new_uid and new_uid != self._uid:
            self._uid = new_uid
            # Commit the UID change to the database
            db.session.commit()

        # If the UID has changed, update the directory name
        if old_uid != self._uid:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_uid)
            new_path = os.path.join(current_app.config['UPLOAD_FOLDER'], self._uid)
            if os.path.exists(old_path):
                os.rename(old_path, new_path)

"""Database Creation and Testing """

# Builds working data set for testing
def initUsers():
    with app.app_context():
        """Create database and tables"""
        db.create_all()
        """Tester data for table"""
        
        u1 = User(name='Thomas Edison', uid=app.config['ADMIN_USER'], password=app.config['ADMIN_PASSWORD'], pfp='toby.png', role="Admin")
        u2 = User(name='Grace Hopper', uid=app.config['DEFAULT_USER'], password=app.config['DEFAULT_PASSWORD'], pfp='hop.png')
        u3 = User(name='Nicholas Tesla', uid='niko', password='123niko', pfp='niko.png' )
        users = [u1, u2, u3]
        
        for user in users:
            try:
                user.create()
            except IntegrityError:
                '''fails with bad or duplicate data'''
                db.session.remove()
                print(f"Records exist, duplicate email, or error: {user.uid}")
