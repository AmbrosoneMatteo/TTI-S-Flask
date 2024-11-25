from flask_login import UserMixin
from .connection import db
from werkzeug.security import generate_password_hash, check_password_hash

user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Relazione many-to-many tra User e Role
    roles = db.relationship('Role', secondary=user_roles, backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)
    
class Resource(db.Model): 
    __tablename__ = "resource"

    id = db.Column(db.Integer, primary_key=True)
    resourceID = db.Column(db.String(60), unique=True, nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey("user.id"),nullable=False)
    prompt = db.Column(db.String(200), nullable=False)
    audio = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Integer, nullable=True)