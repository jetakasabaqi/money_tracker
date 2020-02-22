from flask import request, flash
from config import db, func, app
from flask_bcrypt import Bcrypt
import re
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
SpecialSym =['$', '@', '#', '%'] 

expenses = db.Table('expenses', 
        db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True), 
        db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='cascade', onupdate='cascade'), primary_key=True),
        db.Column('amount', db.Float),
        db.Column('content', db.String),
        db.Column('created_at', db.DateTime, server_default=func.now()),
        db.Column('updated_at', db.DateTime, server_default=func.now(), onupdate=func.now()))

todos = db.Table('todos', 
        db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade'), primary_key=True), 
        db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='cascade', onupdate='cascade'), primary_key=True),
        db.Column('amount', db.Float),
        db.Column('content', db.String(255)),
        db.Column('is_done', db.Boolean),
        db.Column('created_at', db.DateTime, server_default=func.now()),
        db.Column('updated_at', db.DateTime, server_default=func.now(), onupdate=func.now()))
        

class UserExpense(db.Model):
    __tablename__ = 'expenses'
    __table_args__ = {'extend_existing': True} 

class UserTodo(db.Model):
    __tablename__ = 'todos'
    __table_args__ = {'extend_existing': True} 

class User(db.Model):
    __tablename__ = 'users'	
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    monthly_income = db.Column(db.Float)
    created_at = db.Column(db.DateTime, server_default=func.now())   
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
    user_expenses = db.relationship('UserExpense', secondary=expenses, lazy='dynamic',backref=db.backref('expenses_author', lazy=True))
    user_todos = db.relationship('UserTodo', secondary=todos, lazy='dynamic',backref=db.backref('todos_author', lazy=True))
  
    @classmethod
    def validate_user(cls, user_data):
        is_valid = True
        first_name = user_data["first_name"]
        last_name = user_data['last_name']
        passwd = user_data['password']
   
        if len(first_name) < 1:
            is_valid = False
            flash(u'First name cannot be blank.', 'first_name')
        if len(last_name) < 1:
            is_valid = False
            flash(u'Last name cannot be blank.', 'last_name')
        if (not first_name.isalpha() or not last_name.isalpha()) and len(first_name) > 0 and len(last_name) > 0:
            is_valid = False
            flash("First name and last name should contains only letters")
        if len(request.form['email']) < 1:
            flash("Email cannot be blank!", 'email')
        if not EMAIL_REGEX.match(request.form['email']) and len(request.form['email']) > 0:    # test whether a field matches the pattern
            flash("Invalid email address!", 'email')
        if len(passwd) < 8:
            is_valid = False
            flash("Password should be at least 8 characters.")
        if not any(char.isdigit() for char in passwd): 
            is_valid = False
            flash('Password should have at least one numeral')
            
        if not any(char.isupper() for char in passwd): 
            is_valid = False
            flash('Password should have at least one uppercase letter')
            
        if not any(char.islower() for char in passwd): 
            is_valid = False
            flash('Password should have at least one lowercase letter')
            
        if not any(char in SpecialSym for char in passwd):
            is_valid = False
            flash('Password should have at least one of the symbols $@#')
    
        if request.form['password'] != request.form['confirm_password']:
            is_valid = False
            flash("Password doesn't match", 'password')
        return is_valid

    @classmethod
    def add_new_user(cls, user_data):
        hashed_password = bcrypt.generate_password_hash(user_data["password"]).decode('utf-8')
        user_to_add = cls(first_name=user_data["first_name"], last_name=user_data["last_name"], email=user_data["email"], password=hashed_password)
        db.session.add(user_to_add)
        db.session.commit()
        return user_to_add

    @classmethod
    def validate_on_login(cls, user_data):
        result = User.query.filter_by(email=user_data['email']).first_or_404(description="Email doesn't exists")
        is_valid = True
        if len(user_data['email']) < 1:
            is_valid = False
            flash('Email cannot be blank')
        if not bcrypt.check_password_hash(result.password, user_data['password']):
            is_valid = False
            flash('Invalid email or password.')
        return is_valid

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    category_expenses = db.relationship('UserExpense', secondary=expenses, lazy='dynamic',backref=db.backref('expenses_category', lazy=True))
    category_todos = db.relationship('UserTodo', secondary=todos, lazy='dynamic',backref=db.backref('todos_category', lazy=True))

    