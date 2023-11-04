from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired
from flask_wtf.recaptcha import validators
import re

auth = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[validators.Recaptcha()])
    submit = SubmitField('login')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        print(f'email: {email}')

        user = User.query.filter_by(email=email).first()

        print(f'user: {user}')
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('home_views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', form=form, user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


class SignUpForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email()])
    first_name = StringField('firstName', validators=[DataRequired()])
    password1 = PasswordField('password1', validators=[DataRequired()])
    password2 = PasswordField('password2', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[validators.Recaptcha()])
    submit = SubmitField('signUp')


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():

        email = form.email.data
        first_name = form.first_name.data
        password1 = form.password1.data
        password2 = form.password2.data

        user = User.query.filter_by(email=email).first()

        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if user:
            flash('Email already exists.', category='error')
        elif not re.match(pattern, email):
            flash('Please input a valid email address.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('group_views.groups'))

    return render_template("sign_up.html", form=form, user=current_user)
