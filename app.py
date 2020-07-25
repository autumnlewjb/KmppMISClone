from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from date_time import get_datetime
from datetime import datetime, time, timedelta


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
app.config['SQLALCHEMY_BINDS'] = {
    'application': 'sqlite:///application.db',
    'timetable': 'sqlite:///timetable.db'}
app.config['SECRET_KEY'] = 'lewjb2010'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'outing_login'


class Register(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)
    ic_no = db.Column(db.String(200), nullable=True)
    room_no = db.Column(db.String(200), nullable=True)
    tel_no = db.Column(db.String(200), nullable=True)
    hp_no = db.Column(db.String(200), nullable=True)
    course = db.Column(db.String(200), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<student {self.id}>'


class Application(db.Model):
    __bind_key__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, default=datetime.now())
    apply_type = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)
    out_datetime = db.Column(db.DateTime)
    in_datetime = db.Column(db.DateTime)
    transport = db.Column(db.String(200), nullable=False)
    aim = db.Column(db.String(200), nullable=False)
    place = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(100), nullable=False, default='Processing')


class TimeTable(db.Model):
    __bind_key__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(200), nullable=False)
    monday = db.Column(db.String(1000), nullable=True)
    tuesday = db.Column(db.String(1000), nullable=True)
    wednesday = db.Column(db.String(1000), nullable=True)
    thursday = db.Column(db.String(1000), nullable=True)
    friday = db.Column(db.String(1000), nullable=True)

    def __repr__(self):
        return f'<TimeTable for {self.class_name}'


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
            admin = Register.query.filter_by(name='admin').first()
            if admin.is_admin:
                login_user(admin)
                return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], position='admin')
            else:
                return "login failed"
        else:
            return "Invalid username or password."


# User's side
# TODO: temporarily make it log out, find other solution
@app.route('/change/<position>', methods=['GET'])
def change(position):
    dt = get_datetime()
    return render_template('choose_position.html', date=dt['date'], time=dt['time'], day=dt['day'], current_user=current_user)


@app.route('/student', methods=['GET'])
def student():
    return render_template('student/homepage.html')


@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('login.html')


@app.route('/get-number', methods=['GET', 'POST'])
def get_number():
    try:
        num = int(request.form['matrics-no-field'])
        return render_template('student/outing_login.html', num=num)
    except ValueError:
        return redirect('/outing-login')


@app.route('/outing-login', methods=['POST', 'GET'])
def outing_login():
    if request.method == 'POST':
        if request.form['matrics-no-field']:
            matrics_no = request.form['matrics-no-field']
            exist = Register.query.filter_by(matrics_no=matrics_no).first()
            if not exist:
                return 'User not found'
            else:
                login_user(exist)
                print('logged in')
                return redirect('/outing-apply')
        else:
            no = request.form['people-no-field']
            return redirect(f'/group/{no}')
    else:
        return render_template('student/outing_login.html')


@app.route('/outing-apply', methods=['POST', 'GET'])
@login_required
def outing_apply():
    student = current_user
    if request.method == 'POST':
        try:
            in_date = list(map(int, request.form['in-date'].split('-')))
            out_date = list(map(int, request.form['out-date'].split('-')))
            in_time = list(map(int, request.form['in-time'].split(':')))
            out_time = list(map(int, request.form['out-time'].split(':')))
            out_datetime = datetime(year=out_date[0], month=out_date[1], day=out_date[2], hour=out_time[0], minute=out_time[1])
            in_datetime = datetime(year=in_date[0], month=in_date[1], day=in_date[2], hour=in_time[0], minute=in_time[1])
            transport = request.form['transport']
            aim = request.form['aim']
            place = request.form['place']
            apply_type = request.form['apply-type']
            new_application = Application(
                name=student.name,
                matrics_no=student.matrics_no,
                out_datetime=out_datetime,
                in_datetime=in_datetime,
                transport=transport,
                aim=aim,
                place=place,
                apply_type=apply_type
            )
            db.session.add(new_application)
            db.session.commit()
            return redirect('/application-successful')
        except ValueError:
            return '<h1>Application not recorded</h1>'
    else:
        dt = get_datetime()
        timetable = TimeTable.query.filter_by(class_name='F1T05A').first()
        today = datetime.now().strftime('%A').lower()
        try:
            exec('timetable=timetable.{}'.format(today))
            timetable = timetable.split('/')
        except AttributeError:
            timetable = []
            # timetable = timetable.tuesday
            # timetable = timetable.split('/')

        duration = timedelta(hours=1)
        t = datetime(year=1, month=1, day=1, hour=8, minute=0)
        return render_template('student/outing_apply.html', student=current_user, timetable=timetable, day=dt['day'], t=t, duration=duration)


@app.route('/application-successful', methods=['GET', 'POST'])
@login_required
def successful():
    return render_template('student/successful.html', student=current_user)


@app.route('/history')
@login_required
def history():
    previous = Application.query.filter_by(matrics_no=current_user.matrics_no).order_by(Application.datetime).all()
    return render_template('student/history.html', applications=previous)


@app.route('/group/<int:num>', methods=['POST','GET'])
def group(num):
    if request.method == 'POST':
        not_exist = list()
        for i in range(num):
            matrics_no = request.form['matrics-no-{}'.format(i)]
            exist = Register.query.filter_by(matrics_no=matrics_no).first()
            if exist:
                in_date = list(map(int, request.form['in-date'].split('-')))
                out_date = list(map(int, request.form['out-date'].split('-')))
                in_time = list(map(int, request.form['in-time'].split(':')))
                out_time = list(map(int, request.form['out-time'].split(':')))
                out_datetime = datetime(year=out_date[0], month=out_date[1], day=out_date[2], hour=out_time[0], minute=out_time[1])
                in_datetime = datetime(year=in_date[0], month=in_date[1], day=in_date[2], hour=in_time[0], minute=in_time[1])
                transport = request.form['transport']
                aim = request.form['aim']
                place = request.form['place']
                apply_type = request.form['apply-type']
                new_application = Application(
                    name=exist.name,
                    matrics_no=exist.matrics_no,
                    out_datetime=out_datetime,
                    in_datetime=in_datetime,
                    transport=transport,
                    aim=aim,
                    place=place,
                    apply_type=apply_type
                )
                db.session.add(new_application)
                db.session.commit()
            else:
                not_exist.append(matrics_no)
        if len(not_exist):
            return 'User not exist: {}'.format(not_exist)
        else:
            return redirect('/application-successful')
    else:
        return render_template('student/group.html', number=num)


@app.route('/delete-apply/<int:id>', methods=['GET'])
def delete_apply(id):
    to_delete = Application.query.filter_by(id=id).first()
    db.session.delete(to_delete)
    db.session.commit()

    return redirect('/history')


@app.route('/update-apply/<int:id>', methods=['GET', 'POST'])
def update_apply(id):
    to_update = Application.query.filter_by(id=id).first()
    if request.method == 'POST':
        try:
            in_date = list(map(int, request.form['in-date'].split('-')))
            out_date = list(map(int, request.form['out-date'].split('-')))
            in_time = list(map(int, request.form['in-time'].split(':')))
            out_time = list(map(int, request.form['out-time'].split(':')))
            to_update.out_datetime = datetime(year=out_date[0], month=out_date[1], day=out_date[2], hour=out_time[0], minute=out_time[1])
            to_update.in_datetime = datetime(year=in_date[0], month=in_date[1], day=in_date[2], hour=in_time[0], minute=in_time[1])
            to_update.transport = request.form['transport']
            to_update.aim = request.form['aim']
            to_update.place = request.form['place']
            to_update.apply_type = request.form['apply-type']
            to_update.status = "Processing"

            db.session.commit()
            return redirect('/history')
        except ValueError:
            return '<h1>Application not recorded</h1>'
    else:
        return render_template('student/update.html', application=to_update)


# Admin's side
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


@app.route('/approve-all', methods=['GET'])
@login_required
def approve_all():
    to_be_approved_list = Application.query.all()
    for to_be_approved in to_be_approved_list:
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


@app.route('/cancel-all', methods=['GET'])
@login_required
def cancel_all():
    to_be_approved_list = Application.query.all()
    for to_be_approved in to_be_approved_list:
        to_be_approved.status = 'Rejected'

    db.session.commit()

    return redirect('/manage')


@app.route('/register', methods=['POST', 'GET'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form['name']
        matrics_no = request.form['matrics_no']
        ic_no = request.form['ic_no']
        room_no = request.form['room_no']
        tel_no = request.form['tel_no']
        hp_no = request.form['hp_no']
        course = request.form['course']
        new_student = Register(
            name=name,
            matrics_no=matrics_no,
            ic_no=ic_no,
            room_no=room_no,
            tel_no=tel_no,
            hp_no=hp_no,
            course=course
        )

        db.session.add(new_student)
        db.session.commit()
        students = Register.query.order_by(Register.id).all()
        return redirect('/register')
    else:
        students = Register.query.order_by(Register.id).all()
        return render_template('admin/register.html', students=students)


@app.route('/delete-user/<int:id>', methods=['GET'])
def delete_user(id):
    to_delete = Register.query.filter_by(id=id).first()
    db.session.delete(to_delete)
    db.session.commit()
    return redirect('/register')


@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    to_update = Register.query.filter_by(id=id).first()
    if request.method == 'POST':
        to_update.name = request.form['name']
        to_update.matrics_no = request.form['matrics_no']
        to_update.ic_no = request.form['ic_no']
        to_update.room_no = request.form['room_no']
        to_update.tel_no = request.form['tel_no']
        to_update.hp_no = request.form['hp_no']
        to_update.course = request.form['course']

        db.session.commit()
        return redirect('/register')
    else:
        return render_template('admin/update.html', student=to_update)


@app.route('/remove-expired', methods=['GET'])
@login_required
def garbage_collector():
    garbage_bag = [material for material in Application.query.all() if material.out_datetime < datetime.now()]
    for garbage in garbage_bag:
        db.session.delete(garbage)

    db.session.commit()

    return redirect('/manage')


@app.route('/reset-approval', methods=['GET'])
@login_required
def reset_approval():
    application = [material for material in Application.query.all() if material.out_datetime >= datetime.now()]
    for apply in application:
        apply.status = 'Processing'

    db.session.commit()

    return redirect('/manage')


if __name__ == '__main__':
    app.run(debug=True)
