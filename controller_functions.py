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
    expenses = UserExpense.query.filter(UserExpense.user_id == logged_in_user.id).all()
    categories = Category.query.all()


    for exp in expenses:
        for cat in categories:
            if exp.category_id == cat.id:
                exp.category_name = cat.name

    total =0
    today_date = datetime.now()


    # get category name and their percentage based on month 

    
    print(expenses)
    sql = text(f"Select categories.name, count(categories.id) as times from expenses inner join categories on expenses.category_id = categories.id inner join users on expenses.user_id = users.id where users.id = {logged_in_user.id} group by categories.id ")
    result = db.engine.execute(sql)
    categories_by_name_and_percentage = result.fetchall()
    cat_and_percentage = []
    for cat in categories_by_name_and_percentage:
        data = {
            'name': cat.name,
            'percentage': cat.times /len(expenses)
        }
        cat_and_percentage.append(data)
     



    print(cat_and_percentage)


    for ex in expenses:
        total+= ex.amount

    return render_template('viewAll.html', expenses = expenses, total = total, selected = str(today_date.month), categories_percentage = cat_and_percentage)
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
   
    for exp in expenses:
        month = exp.created_at.month

        if(str(month) == selected):
      
            expenses_of_this_month.append(exp)
    categories = Category.query.all()


    for exp in expenses_of_this_month:
        for cat in categories:
            if exp.category_id == cat.id:
                exp.category_name = cat.name

    date = getMonthRange(selected)
  
    sql = text(f"Select categories.name, count(categories.id) as times from expenses inner join categories on expenses.category_id = categories.id inner join users on expenses.user_id = users.id where users.id = {logged_in_user.id} and expenses.created_at BETWEEN '{date[0]}' AND '{date[1]}' group by categories.id ")
 
    categories_by_name_and_percentage = db.engine.execute(sql).fetchall()
   
    cat_and_percentage = []
    for cat in categories_by_name_and_percentage:
        data = {
            'name': cat.name,
            'percentage': cat.times /len(expenses_of_this_month)
        }
        cat_and_percentage.append(data)
    
    return render_template('viewAll.html', expenses = expenses_of_this_month, selected =  selected,  categories_percentage = cat_and_percentage)

def getMonthRange(month):
    print(month)
    switcher = {
        '1': ['2020-01-01 00:00:00','2020-01-31 00:00:00'],
        "2": ['2020-02-01 00:00:00','2020-03-01 00:00:00'],
        "3": ['2020-03-01 00:00:00','2020-03-31 00:00:00'],
        "4": ['2020-04-01 00:00:00','2020-04-30 00:00:00'],
        "5": ['2020-05-01 00:00:00','2020-05-31 00:00:00'],
        "6": ['2020-06-01 00:00:00','2020-06-30 00:00:00'],
        "7": ['2020-07-01 00:00:00','2020-07-31 00:00:00'],
        "8": ['2020-08-01 00:00:00','2020-08-31 00:00:00'],
        "9": ['2020-09-01 00:00:00','2020-09-30 00:00:00'],
        "10": ['2020-10-01 00:00:00','2020-10-31 00:00:00'],
        "11": ['2020-11-01 00:00:00','2020-11-30 00:00:00'],
        "12": ['2020-12-01 00:00:00','2020-12-31 00:00:00']
    }
    func = switcher.get(month, "nothing")
# Execute the function
    return func