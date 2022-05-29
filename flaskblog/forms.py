from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField,DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,NumberRange
from flaskblog.models import User ,Member


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    picture = FileField('Profile Picture for Verification', validators=[FileAllowed(['jpg', 'png']),DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    TimeGap=DecimalField('Gap between consecutive Attendance (in Hours)',
                         validators=[DataRequired(),
                         NumberRange(min=0.01, max=None, message="the time difference must be positive and non zero")] ) #in hours
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_TimeGap(self,TimeGap,min=0.01):
        if TimeGap.data != current_user.time_gap:
            if TimeGap.data<=min:
                raise ValidationError('The time difference must be positive and non zero')

class UpdateMemberAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')



class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')


class MemberForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Profile Picture for Verification', validators=[FileAllowed(['jpg', 'png']),DataRequired()])
    submit = SubmitField('Add Member')

    def validate_username(self, username):
        #in an organisation no username can repeat 
        #but members under differnt admin can have same name 
        member = Member.query.filter_by(username=username.data, user_id=current_user.id).first()
        if member or username.data==current_user.username:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        #email must be unique in whole world(database)
        member = Member.query.filter_by(email=email.data).first()
        email_of_user=User.query.filter_by(email=email.data).first()
        if member or email_of_user:
            raise ValidationError('That email is taken. Please choose a different one.')    

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ConfirmRequestForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Verify')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class RoomIDForm(FlaskForm):
    RoomID = StringField('Room ID',
                           validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Submit')
    def validate_RoomID(self, RoomID):
        user = User.query.filter_by(id=RoomID.data).first()
        if user is None:
            raise ValidationError('There is no Room with that ID. You must register first.')