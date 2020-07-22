from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from date_time import get_datetime
from flask_login import login_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
db = SQLAlchemy(app)


class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    matrics_no = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<student {self.id}>'


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
        return render_template('apply.html', student=exist)


if __name__ == '__main__':
    app.run(debug=True)
