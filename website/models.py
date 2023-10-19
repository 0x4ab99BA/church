from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField

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
    posts = db.relationship('Post', back_populates='user')  # Add this line to establish the relationship with Post


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.Text(500))
    creator = db.Column(db.String(150))
    time = db.Column(db.DateTime, default=datetime.now)
    subscribers = db.relationship('User', secondary=user_group, back_populates='subscriptions')
    posts = db.relationship('Post', back_populates='group')  # Add this line to establish the relationship with Post


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey to link Post and User
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)  # ForeignKey to link Post and Group
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', back_populates='posts')
    group = db.relationship('Group', back_populates='posts')


class BannerUploadForm(FlaskForm):
    banner = FileField('Upload Banner Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField('Upload')


class GroupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    creator = StringField('creator', validators=[Optional()])
    submit = SubmitField('submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = CKEditorField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')
