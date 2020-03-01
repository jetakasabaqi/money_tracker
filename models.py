from flask import request, flash
from config import db, func, app
from flask_bcrypt import Bcrypt
import re
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{5,}$')
SpecialSym =['$', '@', '#', '%'] 

expenses = db.Table('expenses', 
        db.Column('id', db.Integer, primary_key=True),
        db.Column('todo_id', db.Integer, default=0),
        db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade')), 
        db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='cascade', onupdate='cascade')),
        db.Column('amount', db.Float),
        db.Column('content', db.String),
        db.Column('created_at', db.DateTime, server_default=func.now()),
        db.Column('updated_at', db.DateTime, server_default=func.now(), onupdate=func.now()))

todos = db.Table('todos', 
        db.Column('id', db.Integer, primary_key=True),
        db.Column('user_id', db.Integer, db.ForeignKey('users.id', ondelete='cascade', onupdate='cascade')), 
        db.Column('category_id', db.Integer, db.ForeignKey('categories.id', ondelete='cascade', onupdate='cascade')),
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
    user_expenses = db.relationship('UserExpense',  lazy=True,backref=db.backref('expenses_author'))
    user_todos = db.relationship('UserTodo',lazy=True,backref=db.backref('todos_author'))
  
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
            is_valid = False
            flash("Invalid email address!", 'email')
        if len(user_data["monthly_income"]) < 1:
            is_valid = False
            flash('Monthly income cannot be null','monthly_income')
        if not user_data["monthly_income"].isdigit():
            is_valid = False
            flash('Monthly income must be a number','monthly_income')
        if not PASSWORD_REGEX.match(request.form['password'] ):
            is_valid = False
            flash("Password must have at least 5 characters, one number, one uppercase character, one special symbol.",'password')


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
      #  result = User.query.filter_by(email=user_data['email']).first_or_404(description="Email doesn't exists")
        is_valid = True
        if len(user_data['email']) < 1:
            is_valid = False
            flash('Email cannot be blank','email')
        if len(user_data['password']) <1:
            is_valid = False
            flash('Passoword cannot be blank','password')
        if is_valid :
            user = User.query.filter_by(email=user_data['email']).first()
            if user:
                if not bcrypt.check_password_hash(user.password, user_data['password']):
                    is_valid = False
                    flash('Invalid email or password.','login_error')
        return is_valid

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    category_expenses = db.relationship('UserExpense',  lazy=True,backref=db.backref('expenses_category'))
    category_todos = db.relationship('UserTodo', lazy=True,backref=db.backref('todos_category'))

