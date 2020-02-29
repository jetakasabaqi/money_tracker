from flask import render_template, request, redirect, session
from config import app, db
from models import User, Category, UserExpense, UserTodo, expenses
from flask_bcrypt import Bcrypt
from datetime import datetime
app.secret_key = 'secret'
bcrypt = Bcrypt(app)

from sqlalchemy import text
from sqlalchemy.orm import scoped_session, sessionmaker


def landing_page():
   
    return render_template("index.html")

def register():
    if 'user_id' in session:
        return render_template("home.html")
    else:
        return render_template("register.html")


def login():
    if 'user_id' in session:
        return redirect("/home")
    else:
        return render_template("login.html")

def home():
    if 'user_id' in session:
        logged_in_user = User.query.filter_by(id=session['user_id']).first()
        categories = Category.query.all()
        sql = text("SELECT e.*, c.name as category_name, strftime('%Y', e.updated_at) AS year, strftime('%m', e.updated_at) AS month, strftime('%d', e.updated_at) AS day FROM expenses e JOIN categories c ON e.category_id = c.id WHERE e.user_id = "+str(session['user_id'])+" ORDER BY e.updated_at DESC LIMIT 5")
        result = db.engine.execute(sql)
        expenses = result.fetchall()   
        return render_template("home.html", expenses=expenses, logged_in_user=logged_in_user, categories=categories)
    else:
        return redirect('/login')

def on_register():
    validation_check = User.validate_user(request.form)       
    if not validation_check:
        return redirect('/register')
    else:
        if request.form:
            new_user = User.add_new_user(request.form)
            session['user_id'] = new_user.id
        return redirect('/home')

def on_login():
    validation_check = User.validate_on_login(request.form)
    if not validation_check:
        return redirect('/login')
    else:
        result = User.query.filter_by(email=request.form.get('email')).first_or_404(description="Email doesn't exist")
        session['user_id'] = result.id
        return redirect('/home')

def logout():
    session.clear()
    return redirect('/')

def my_expenses():
    logged_in_user = User.query.filter_by(id=session['user_id']).first_or_404("Not logged in")
    expenses = UserExpense.query.filter(UserExpense.user_id==session['user_id']).all()
    return render_template("user_expenses.html", expenses=expenses, logged_in_user=logged_in_user)

def create_expense():
    name = request.form.get("expense_name")
    amount = request.form.get("expense_price")
    category_id = int(request.form.get("category_id"))
    new_expense = UserExpense(user_id=session['user_id'], category_id=category_id, amount=amount, content=name)
    db.session.add(new_expense)
    db.session.commit()
    return redirect('/home')

def viewAllExpences():
    logged_in_user = User.query.filter_by(id = session['user_id']).first_or_404("Not logged in")
    expenses = UserExpense.query.filter(UserExpense.user_id == session['user_id']).all()
    categories = Category.query.all()


    for exp in expenses:
        for cat in categories:
            if exp.category_id == cat.id:
                exp.category_name = cat.name

    total =0
    today_date = datetime.now()

    for ex in expenses:
        total+= ex.amount

    return render_template('viewAll.html', expenses = expenses, total = total, selected = str(today_date.month))
def editExpense(id):
    expense = UserExpense.query.filter_by(id = id).first()

    return render_template('editExpense.html', expense = expense)

def editExpenseForm():
    print(request.form['expense_id'])
    expense = UserExpense.query.filter_by(id = request.form['expense_id']).first()
    expense.content = request.form['expense_name']
    expense.amount = request.form['expense_price']
    print(expense)
    db.session.commit()

    return redirect('/view_all')
def deleteExpense(ex_id):
    logged_in_user = User.query.filter_by(id=session['user_id']).first()
    expenses = logged_in_user.user_expenses
    expense = UserExpense.query.filter_by(id=ex_id).first()
    expenses.remove(expense)
    db.session.commit()
    return redirect('/view_all')
def filterExpense():
    logged_in_user = User.query.filter_by(id=session['user_id']).first()
    expenses = logged_in_user.user_expenses
    expenses_of_this_month = []
    selected = request.form['active_months']
    print(request.form['active_months'])
    for exp in expenses:
        month = exp.created_at.month
        print('month', month)
        print('form', request.form['active_months'])
        if(str(month) == selected):
            print('true')
            expenses_of_this_month.append(exp)
    print(expenses_of_this_month)
    print(selected)
    return render_template('viewAll.html', expenses = expenses_of_this_month, selected =  selected)