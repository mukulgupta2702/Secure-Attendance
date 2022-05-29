from datetime import datetime
from flaskblog import db, login_manager, app
from flask_login import UserMixin
from random import randint
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True,default=randint(000000,999999), unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    email_confirmed = db.Column(db.Boolean(), nullable=False, default=False)
    time_gap=db.Column(db.Float,default=0.01, nullable=False) #in hours

    members=db.relationship('Member', backref='admin', lazy=True)
    alerts=db.relationship('Alert', backref='author', lazy=True)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    def get_mail_confirm_token(self):
        s = Serializer(app.config["SECRET_KEY"], salt="email-comfirm")
        return s.dumps(self.email, salt="email-confirm")

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        #token expires in 30 minutes
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, expires_sec)['user_id']
        except:
            return None
        return User.query.get(user_id)
        
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


    @staticmethod
    def verify_mail_confirm_token(token):
        s = Serializer(app.config["SECRET_KEY"], salt="email-confirm")
        try:
            email = s.loads(token, salt="email-confirm", max_age=3600)
            #token expires in 1 hour
        except :
            return None
        return email


class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    email = db.Column(db.String(120), unique=True, nullable=False)
    attendance_count=db.Column(db.Integer, default=0,nullable=False)
    attendance_time=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.username}', '{self.email}')"

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
