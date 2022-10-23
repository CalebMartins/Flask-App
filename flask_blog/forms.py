from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from flask_blog.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password',validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email already exists')
    
            

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password',validators=[DataRequired()])
    remember = BooleanField(label='Remember Me')
    submit = SubmitField(label='Sign In')

class UpdateAccountForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    photo = FileField(label='Update Profile Picture(optional)', validators=[FileAllowed(['jpg', 'png', 'bmp'])])
    submit = SubmitField(label='Update')

    # creating custom validators
    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken')
        
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email already exists')

class PostForm(FlaskForm):
    content = TextAreaField(label='Write Post', validators=[DataRequired()])
    submit = SubmitField(label='Post')

class CommentForm(FlaskForm):
    comment = TextAreaField(label='comment', validators=[DataRequired()])
    submit = SubmitField(label='Post')

class UpdatePostForm(FlaskForm):
    content = TextAreaField(label='comment', validators=[DataRequired()])
    submit = SubmitField(label='Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired() ,Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user == None:
            raise ValidationError('There\'s no account with this email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password',validators=[DataRequired()])
    confirm_password = PasswordField(label='Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Change Password')

