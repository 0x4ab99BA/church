from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed

user_group = db.Table(
    'user_group',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    subscriptions = db.relationship('Group', secondary=user_group, back_populates='subscribers')


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.Text(500))
    creator = db.Column(db.String(150))
    time = db.Column(db.DateTime, default=datetime.now)
    subscribers = db.relationship('User', secondary=user_group, back_populates='subscriptions')


class BannerUploadForm(FlaskForm):
    banner = FileField('Upload Banner Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Upload')


class GroupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    creator = StringField('creator', validators=[Optional()])
    submit = SubmitField('submit')
