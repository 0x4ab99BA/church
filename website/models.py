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
    admin = db.Column(db.Boolean, default=False)
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey to link Post and User
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)  # ForeignKey to link Post and Group
    created_at = db.Column(db.DateTime, default=datetime.now)

    files = db.relationship('File', back_populates='post')
    user = db.relationship('User', back_populates='posts')
    group = db.relationship('Group', back_populates='posts')
    likes = db.relationship('Like', backref='post', lazy='dynamic')

    def like_count(self):
        return self.likes.count()


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', back_populates='files')


class GroupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = StringField('description', validators=[DataRequired()])
    creator = StringField('creator', validators=[Optional()])
    submit = SubmitField('submit')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 评论者的用户id
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # 评论的帖子id
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))  # 评论的父评论id，如果是针对帖子的评论，则为None
    timestamp = db.Column(db.DateTime, default=datetime.now)  # 评论时间

    user = db.relationship('User', backref='comments')  # 与User模型建立关系，方便查询评论者信息
    post = db.relationship('Post', backref='comments')  # 与Post模型建立关系，方便查询评论所属的帖子信息
    parent = db.relationship('Comment', remote_side=[id], backref='children')



class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)
