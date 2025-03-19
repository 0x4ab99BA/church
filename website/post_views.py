import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from bs4 import BeautifulSoup

from . import db
from .models import Group, PostForm, Post, File, Comment, Like, CommentForm
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

        for like in post_to_delete.likes:
            db.session.delete(like)

        for comment in post_to_delete.comments:
            db.session.delete(comment)

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
    if extension not in ['pdf', 'pptx', 'ppt']:
        return upload_fail(message='PDF and PPT only!')
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

    return jsonify({'status': 'success'})


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

    if post.user_id != current_user.id and current_user.admin is False:

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


@post_views.route('/group/<int:group_id>/show_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def show_post(post_id, group_id):
    # 根据post_id查询帖子对象
    post = Post.query.get_or_404(post_id)
    group = Group.query.get_or_404(group_id)

    form = CommentForm()
    comment_form = CommentForm()

    reversed_comments = reversed([comment for comment in post.comments if comment.parent_id is None])

    if form.validate_on_submit():
        body = form.comment_body.data
        new_comment = Comment(body=body, user=current_user, post=post)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('post_views.show_post', post_id=post_id, group_id=group_id))

    return render_template('post.html',
                           post=post, user=current_user, group=group,
                           form=form, comment_form=comment_form,
                           reversed_comments=reversed_comments)


@post_views.route('/like_post', methods=['POST'])
@login_required
def like_post():
    data = json.loads(request.data)
    post_id = data['postId']

    post = Post.query.get_or_404(post_id)
    liked = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if not liked:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        likes = post.like_count()

        return jsonify({'status': 'success', 'updatedLikeCount': likes})

    else:
        db.session.delete(liked)
        db.session.commit()
        likes = post.like_count()

        return jsonify({'status': 'success', 'updatedLikeCount': likes})


@post_views.route('/submit_comment', methods=['POST'])
@login_required
def submit_comment():
    if request.method == 'POST':
        comment_body = request.form['comment_body']
        post_id = request.form['post_id']
        parent_comment_id = request.form['parent_comment_id']

        if parent_comment_id == '0':
            parent_comment_id = None

        post = Post.query.get_or_404(post_id)
        form = CommentForm()
        comment_form = CommentForm()

        new_comment = Comment(body=comment_body, user_id=current_user.id, post_id=post_id, parent_id=parent_comment_id)
        db.session.add(new_comment)
        db.session.commit()

        reversed_comments = reversed([comment for comment in post.comments if comment.parent_id is None])
        return render_template('comments_partial.html',
                               post=post, user=current_user,
                               form=form, comment_form=comment_form,
                               reversed_comments=reversed_comments)


@post_views.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required  # 确保只有登录用户可以删除评论
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    # 确保当前用户是评论的作者或有其他权限
    if current_user.id != comment.user_id and not current_user.admin:
        flash("cannot delete other's comment", category='error')
    else:
        # 删除评论及其子评论
        Comment.query.filter_by(parent_id=comment_id).delete()
        db.session.delete(comment)
        db.session.commit()
    return jsonify(success=True)

