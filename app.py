from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
db = SQLAlchemy(app)


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
        user = Login(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        return render_template('homepage.html', username=username, password=password)


if __name__ == '__main__':
    app.run(debug=True)
