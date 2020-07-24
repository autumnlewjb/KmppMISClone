from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from date_time import get_datetime
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
app.config['SQLALCHEMY_BINDS'] = {'application': 'sqlite:///application.db'}
app.config['SECRET_KEY'] = 'lewjb2010'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'outing_login'


class Register(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

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
    status = db.Column(db.String(100), nullable=False, default='Processing')


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
            return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], position='student')
        elif username == 'admin' and password == 'adminkmpp':
            dt = get_datetime()
            admin = Register.query.filter_by(matrics_no=password).first()
            if admin.is_admin:
                login_user(admin)
                return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], position='admin')
        else:
            return "Invalid username or password."


# User's side
# TODO: this don't work right for the admin page
@app.route('/change/<position>', methods=['GET'])
def change(position):
    dt = get_datetime()
    return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], position=position)


@app.route('/student', methods=['GET'])
def student():
    return render_template('student/homepage.html')


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/outing-login', methods=['POST', 'GET'])
def outing_login():
    if request.method == 'POST': 
        matrics_no = request.form['matrics-no-field']
        exist = Register.query.filter_by(matrics_no=matrics_no).first()
        if not exist:
            return 'User not found'
        else:
            login_user(exist)
            print('logged in')
            return redirect('/outing-apply')
    else:
        return render_template('student/outing_login.html')


@app.route('/outing-apply', methods=['POST', 'GET'])
@login_required
def outing_apply():
    student = current_user
    if request.method == 'POST':
        out_date = '{day}/{month}/{year}'.format(day=request.form['out-day'], month=request.form['out-month'], year=request.form['out-year'])
        in_date = '{day}/{month}/{year}'.format(day=request.form['in-day'], month=request.form['in-month'], year=request.form['in-year'])
        new_application = Application(name=student.name, matrics_no=student.matrics_no, out_date=out_date, in_date=in_date)
        db.session.add(new_application)
        db.session.commit()
        return redirect('/application-successful')
    else:
        return render_template('student/outing_apply.html', student=current_user)


@app.route('/application-successful', methods=['GET', 'POST'])
@login_required
def successful():
    logout_user()
    return render_template('student/successful.html', student=current_user)


@app.route('/history')
@login_required
def history():
    previous = Application.query.filter_by(matrics_no=current_user.matrics_no).order_by(Application.datetime).all()
    return render_template('student/history.html', applications=previous)


# Admin's side
# def change():
#     dt = get_datetime()
#     return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], position='admin')


@app.route('/admin-homepage', methods=['GET'])
@login_required
def admin_homepage():
    return render_template('admin/homepage.html')


@app.route('/manage', methods=['GET'])
@login_required
def manage():
    applications = Application.query.order_by(Application.datetime).all()
    return render_template('admin/manage.html', applications=applications)


@app.route('/approve/<int:id>', methods=['GET'])
@login_required
def approve(id):
    to_be_approved = Application.query.get_or_404(id)
    to_be_approved.status = 'Approved'

    db.session.commit()

    return redirect('/manage')


@app.route('/cancel/<int:id>', methods=['GET'])
@login_required
def cancel(id):
    to_be_cancelled = Application.query.get_or_404(id)
    to_be_cancelled.status = 'Rejected'

    db.session.commit()

    return redirect('/manage')


@app.route('/register', methods=['POST', 'GET'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form['name']
        matrics_no = request.form['matrics_no']
        new_student = Register(name=name, matrics_no=matrics_no)

        db.session.add(new_student)
        db.session.commit()
        students = Register.query.order_by(Register.id).all()
        return redirect('/register')
    else:
        students = Register.query.order_by(Register.id).all()
        return render_template('admin/register.html', students=students)


if __name__ == '__main__':
    app.run(debug=True)
