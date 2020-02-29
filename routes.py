from flask import Flask
from config import app
from controller_functions import (landing_page, register, login, on_register, on_login, logout,
home, create_expense, viewAllExpences, filterExpense, editExpense, deleteExpense, editExpenseForm,
todo, create_todo, checkToDo, uncheckToDo, destroyToDo)

app.add_url_rule("/", view_func=landing_page)
app.add_url_rule("/register", view_func=register)
app.add_url_rule("/login", view_func=login)
app.add_url_rule('/home', view_func = home)
app.add_url_rule("/register_user", view_func=on_register, methods=['POST'])
app.add_url_rule("/login_user", view_func=on_login, methods=['POST'])
app.add_url_rule("/logout", view_func=logout)
app.add_url_rule("/create_expense", view_func=create_expense, methods=['POST'])
app.add_url_rule("/view_all", view_func=viewAllExpences)
app.add_url_rule("/edit/<id>", view_func=editExpense)
app.add_url_rule("/edit-expense", view_func=editExpenseForm, methods=['POST'])
app.add_url_rule("/delete/<ex_id>", view_func=deleteExpense)
app.add_url_rule("/filter-expense", view_func=filterExpense, methods=['POST'])
app.add_url_rule("/toDoList", view_func=todo)
app.add_url_rule("/create-todo", view_func=create_todo, methods=['POST'])
app.add_url_rule("/check-todo/<int:todo_id>", view_func=checkToDo)
app.add_url_rule("/uncheck-todo/<int:todo_id>", view_func=uncheckToDo)
app.add_url_rule("/destroy-todo/<int:todo_id>", view_func=destroyToDo)





