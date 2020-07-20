from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from date_time import get_datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
db = SQLAlchemy(app)


malay = {
    'Sun': 'AHAD',
    'Mon': 'ISNIN',
    'Tue': 'SELASA',
    'Wed': 'RABU',
    'Thu': 'KHAMIS',
    'Fri': 'JUMAAT',
    'Sat': 'SABTU',
}


class Login(db.Model):
    username = db.Column(db.String(200), nullable=False, primary_key=True)
    password = db.Column(db.String(200), nullable=False)


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        if username == 'pelajar' and password == 'pelajarkmpp':
            dt = get_datetime()
            return render_template('homepage.html', date=dt['date'], time=dt['time'], day=dt['day'])
        else:
            return "Invalid username or password."


@app.route('/student', methods=['GET'])
def student():
    return render_template('student.html')


@app.route('/logout', methods=['GET'])
def logout():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
