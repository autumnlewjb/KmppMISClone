from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from date_time import get_datetime
from datetime import datetime
import time


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
app.config['SQLALCHEMY_BINDS'] = {'application': 'sqlite:///application.db'}
app.config['SECRET_KEY']='lewjb2010'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'outing'


class Register(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<student {self.id}>'


class Application(db.Model):
    __bind_key__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.now())
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)
    out_date = db.Column(db.String(200), nullable=False)
    in_date = db.Column(db.String(200), nullable=False)


@login_manager.user_loader
def load_user(id):
    return Register.query.get(id)


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
        elif username == 'admin' and password == 'adminkmpp':
            students = Register.query.order_by(Register.id).all()
            return render_template('admin.html', students=students)
        else:
            return "Invalid username or password."


# TODO: this don't work right
@app.route('/change', methods=['GET'])
def change():
    return render_template('homepage.html')


@app.route('/student', methods=['GET'])
def student():
    return render_template('student.html')


@app.route('/logout', methods=['GET'])
def logout():
    return render_template('login.html')


@app.route('/outing', methods=['GET'])
def outing():
    return render_template('outing.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        matrics_no = request.form['matrics_no']
        new_student = Register(name=name, matrics_no=matrics_no)

        db.session.add(new_student)
        db.session.commit()
        students = Register.query.order_by(Register.id).all()
        return render_template('admin.html', students=students)
    else:
        students = Register.query.order_by(Register.id).all()
        return render_template('admin.html', students=students)


@app.route('/check-no', methods=['POST', 'GET'])
def check_no():
    matrics_no = request.form['matrics-no-field']
    exist = Register.query.filter_by(matrics_no=matrics_no).first()
    if not exist:
        return 'User not found'
    else:
        login_user(exist)
        print('logged in')
        return redirect('/apply-outing')


@app.route('/apply-outing', methods=['POST', 'GET'])
@login_required
def apply_outing():
    student = current_user
    if request.method == 'POST':
        out_date = '{day}/{month}/{year}'.format(day=request.form['out-day'], month=request.form['out-month'], year=request.form['out-year'])
        in_date = '{day}/{month}/{year}'.format(day=request.form['in-day'], month=request.form['in-month'], year=request.form['in-year'])
        new_application = Application(name=student.name, matrics_no=student.matrics_no, out_date=out_date, in_date=in_date)
        db.session.add(new_application)
        db.session.commit()
        return redirect('/application-successful')
    else:
        return render_template('apply.html', student=current_user)


@app.route('/application-successful', methods=['GET', 'POST'])
@login_required
def successful():
    logout_user()
    return render_template('successful.html', student=current_user)


if __name__ == '__main__':
    app.run(debug=True)
