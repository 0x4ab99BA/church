import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user

from . import db
from .models import Group, Note, GroupForm, PostForm, Post, User
from flask_ckeditor import upload_success, upload_fail
from werkzeug.utils import secure_filename
import uuid as uuid
import os

views = Blueprint('views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))


@views.route('/', methods=['GET', 'POST'])
# @views.route('/home', methods=['GET', 'POST'])
@login_required
def home():

    if current_user.is_authenticated:
        subscribed_groups = current_user.subscriptions

        latest_posts = []
        for group in subscribed_groups:
            group_posts = Post.query.filter_by(group_id=group.id).order_by(Post.created_at.desc()).limit(4).all()
            if group_posts:
                latest_posts.extend(group_posts)

        latest_posts.sort(key=lambda post: post.created_at, reverse=True)
        latest_4_posts = latest_posts[:4]

        return render_template('home.html',
                               latest_posts=latest_4_posts,
                               user=current_user,
                               subscribed_groups=subscribed_groups)

    return redirect(url_for('auth.login'))


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)  # this function expects a JSON from the INDEX.js file
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    page = request.args.get('page', 1, type=int)
    per_page = 4  # Number of items per page

    groups = Group.query.paginate(page=page, per_page=per_page)
    return render_template("groups.html", user=current_user, groups=groups)


@views.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()

    if form.validate_on_submit():

        name = form.name.data
        description = form.description.data
        creator = current_user.first_name

        group = Group.query.filter_by(name=name).first()

        if group:
            flash('Group already exists.', category='error')
        else:
            new_group = Group(name=name, description=description, creator=creator)
            db.session.add(new_group)
            db.session.commit()
            flash('Group created!', category='success')
            return redirect(url_for('views.groups'))

    return render_template("create_group.html", form=form, user=current_user)


@views.route('/subscribe/<int:group_id>', methods=['POST'])
@login_required
def subscribe(group_id):
    group = Group.query.get(group_id)
    user = current_user
    user.subscriptions.append(group)
    db.session.commit()
    return redirect(url_for('views.groups'))


@views.route('/unsubscribe/<int:group_id>', methods=['POST'])
@login_required
def unsubscribe(group_id):
    group = Group.query.get(group_id)
    user = current_user
    user.subscriptions.remove(group)
    db.session.commit()
    return redirect(url_for('views.groups'))


@views.route('/group/<int:group_id>/content', methods=['GET', 'POST'])
@login_required
def group_content(group_id):
    group = Group.query.get(group_id)
    form = PostForm()
    posts = Post.query.filter_by(group_id=group_id).all()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        print('body: ', body)

        post = Post(title=title, content=body, user_id=current_user.id, group_id=group_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('views.group_content', group_id=group_id))

    return render_template('group_content.html', form=form, group=group, user=current_user, posts=posts)


@views.route('/files/<filename>')
@login_required
def uploaded_files(filename):
    path = os.path.join(basedir, 'uploads')
    return send_from_directory(path, filename)


@views.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['pdf']:
        return upload_fail(message='PDF only!')
    pic_filename = secure_filename(f.filename)
    pic_name = str(uuid.uuid1()) + '_' + pic_filename
    f.save(os.path.join(os.path.join(basedir, 'uploads'), pic_name))
    url = url_for('views.uploaded_files', filename=pic_name)
    return upload_success(url, filename=pic_name)


@views.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    pic_filename = secure_filename(f.filename)
    pic_name = str(uuid.uuid1()) + '_' + pic_filename
    f.save(os.path.join(os.path.join(basedir, 'uploads'), pic_name))
    url = url_for('views.uploaded_files', filename=pic_name)
    return upload_success(url, filename=pic_name)


@views.errorhandler(413)
@login_required
def too_large(e):
    return upload_fail(message='File is too large!')
