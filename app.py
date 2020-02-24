from config import app
import routes


from flask import Flask,render_template
app = Flask("__mame__")

if __name__ == "__main__":
    app.run(debug=True)