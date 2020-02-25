from flask import Flask
from config import app
from controller_functions import (landing_page, register, login, on_register, on_login, logout,home)

app.add_url_rule("/", view_func=landing_page)
app.add_url_rule("/register", view_func=register)
app.add_url_rule("/login", view_func=login)
app.add_url_rule('/home', view_func = home)
app.add_url_rule("/register_user", view_func=on_register, methods=['POST'])
app.add_url_rule("/login_user", view_func=on_login, methods=['POST'])
app.add_url_rule("/logout", view_func=logout)

