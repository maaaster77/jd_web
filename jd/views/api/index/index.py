from flask import jsonify, render_template

from jd import app


@app.route('/')
def index():
    return render_template('login.html')