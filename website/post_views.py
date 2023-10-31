import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from bs4 import BeautifulSoup

from . import db
from .models import Group, PostForm, Post, File
from flask_ckeditor import upload_success, upload_fail
from werkzeug.utils import secure_filename
import uuid as uuid
import os

post_views = Blueprint('post_views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))


def delete_post_and_files(post_to_delete):
    try:
        for file in post_to_delete.files:
            file_path = os.path.join(basedir, 'uploads', file.content)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                pass
            db.session.delete(file)
        db.session.delete(post_to_delete)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise Exception("Error occurred while deleting post")


@post_views.route('/files/<filename>')
@login_required
def uploaded_files(filename):
    path = os.path.join(basedir, 'uploads')
    return send_from_directory(path, filename)


@post_views.route('/upload', methods=['POST'])
@login_required
def upload():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['pdf']:
        return upload_fail(message='PDF only!')
    pic_filename = secure_filename(f.filename)
    pic_name = str(uuid.uuid1()) + '_' + pic_filename
    f.save(os.path.join(os.path.join(basedir, 'uploads'), pic_name))
    url = url_for('post_views.uploaded_files', filename=pic_name)
    return upload_success(url, filename=pic_name)


@post_views.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    f = request.files.get('upload')
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    pic_filename = secure_filename(f.filename)
    pic_name = str(uuid.uuid1()) + '_' + pic_filename
    f.save(os.path.join(os.path.join(basedir, 'uploads'), pic_name))
    url = url_for('post_views.uploaded_files', filename=pic_name)
    return upload_success(url, filename=pic_name)


@post_views.errorhandler(413)
@login_required
def too_large(e):
    return upload_fail(message='File is too large!')


@post_views.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    post = json.loads(request.data)
    post_id = post['postId']
    post_to_delete = db.session.query(Post).filter_by(id=post_id).first()

    if post_to_delete:
        if post_to_delete.user_id == current_user.id or current_user.admin:
            delete_post_and_files(post_to_delete)
        else:
            flash("Cannot delete other's post.", category='error')

    return jsonify({'success': True})


@post_views.route('/group/<int:group_id>/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(group_id, post_id):
    group = Group.query.get(group_id)
    post = Post.query.filter_by(id=post_id, group_id=group_id).first()

    images_and_files = []
    for file in post.files:
        images_and_files.append(file.content)

    if post is None:
        flash('Post not found or does not belong to this group', 'error')
        return redirect(url_for('group_views.group_content', group_id=group_id))

    if post.user_id != current_user.id or current_user.admin is False:
        flash('You do not have permission to edit this post', 'error')
        return redirect(url_for('group_views.group_content', group_id=group_id))

    form = PostForm()

    if form.validate_on_submit():

        post.title = form.title.data
        post.content = form.body.data

        db.session.commit()

        uploaded_images_and_files = []

        soup = BeautifulSoup(form.body.data, 'html.parser')
        a_tags = soup.find_all('a')
        href_contents = [a['href'].replace('/files/', '') for a in a_tags if a.get('href', '').startswith('/files/')]

        uploaded_images_and_files.extend(href_contents)

        img_tags = soup.find_all('img')
        src_contents = [img['src'].replace('/files/', '') for img in img_tags if
                        img.get('src', '').startswith('/files/')]

        uploaded_images_and_files.extend(src_contents)

        file_to_delete = [file for file in images_and_files if file not in uploaded_images_and_files]
        file_to_add = [file for file in uploaded_images_and_files if file not in images_and_files]

        for url in file_to_delete:
            for file in post.files:
                if url == file.content:
                    file_path = os.path.join(basedir, 'uploads', file.content)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        pass
                    db.session.delete(file)
                    db.session.commit()

        for content in file_to_add:
            file = File(content=content, post_id=post.id)
            db.session.add(file)
            db.session.commit()

        return redirect(url_for('group_views.group_content', group_id=group_id))

    form.title.data = post.title
    form.body.data = post.content

    return render_template('edit_post.html', form=form, group=group, user=current_user, post=post)
