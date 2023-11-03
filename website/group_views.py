import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from bs4 import BeautifulSoup

from . import db
from .models import Group, GroupForm, PostForm, Post, File
from .forms import SubscriptionForm
import os

group_views = Blueprint('group_views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))


@group_views.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # Number of items per page

    form = SubscriptionForm()
    groups = Group.query.paginate(page=page, per_page=per_page)
    return render_template("groups.html", user=current_user, groups=groups, form=form)


@group_views.route('/create_group', methods=['GET', 'POST'])
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
            return redirect(url_for('group_views.groups'))

    return render_template("create_group.html", form=form, user=current_user)


@group_views.route('/edit_group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    form = GroupForm()
    group = Group.query.get(group_id)

    if current_user.admin is False:
        flash('You do not have permission to edit this group', 'error')
        return redirect(url_for('views.groups'))

    if form.validate_on_submit():

        name = form.name.data
        description = form.description.data
        creator = current_user.first_name

        group_same_name = Group.query.filter_by(name=name).first()

        if group_same_name and name != group.name:
            flash('Group already exists.', category='error')
        else:
            group.name = name
            group.description = description
            group.creator = creator

            db.session.commit()
            flash('Group changed!', category='success')
            return redirect(url_for('group_views.groups'))

    form.name.data = group.name
    form.description.data = group.description
    form.creator.data = group.creator

    return render_template("create_group.html", form=form, user=current_user)


@group_views.route('/delete_group', methods=['POST'])
@login_required
def delete_group():
    group = json.loads(request.data)
    group_id = group['groupId']
    group_to_delete = Group.query.get(group_id)

    if group_to_delete:
        if current_user.admin:
            try:
                # 获取属于该组的所有帖子
                posts_to_delete = Post.query.filter_by(group_id=group_id).all()

                if posts_to_delete:
                    flash("cannot delete a group that contains posts..", category='error')
                else:
                    db.session.delete(group_to_delete)
                    db.session.commit()
                    flash("Group deleted successfully.", category='success')
            except Exception as e:
                db.session.rollback()
                flash("Error occurred while deleting group and associated posts.", category='error')
        else:
            flash("You don't have permission to delete this group.", category='error')
    else:
        flash("Group not found.", category='error')

    return jsonify('success')


@group_views.route('/subscribe/<int:group_id>', methods=['POST'])
@login_required
def subscribe(group_id):
    form = SubscriptionForm()

    if form.validate_on_submit():
        group = Group.query.get(group_id)
        user = current_user
        user.subscriptions.append(group)
        db.session.commit()
    return redirect(url_for('group_views.groups'))


@group_views.route('/unsubscribe/<int:group_id>', methods=['POST'])
@login_required
def unsubscribe(group_id):
    form = SubscriptionForm()
    if form.validate_on_submit():
        group = Group.query.get(group_id)
        user = current_user
        user.subscriptions.remove(group)
        db.session.commit()
    return redirect(url_for('group_views.groups'))


@group_views.route('/group/<int:group_id>/content', methods=['GET', 'POST'])
@login_required
def group_content(group_id):
    group = Group.query.get(group_id)
    form = PostForm()

    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(group_id=group_id).order_by(Post.created_at.desc()).paginate(page=page, per_page=8)

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        # print('body: ', body)

        post = Post(title=title, content=body, user_id=current_user.id, group_id=group_id)
        db.session.add(post)
        db.session.commit()

        uploaded_images_and_files = []

        soup = BeautifulSoup(body, 'html.parser')
        a_tags = soup.find_all('a')
        href_contents = [a['href'].replace('/files/', '') for a in a_tags if a.get('href', '').startswith('/files/')]

        uploaded_images_and_files.extend(href_contents)

        img_tags = soup.find_all('img')
        src_contents = [img['src'].replace('/files/', '') for img in img_tags if
                        img.get('src', '').startswith('/files/')]

        uploaded_images_and_files.extend(src_contents)

        for content in uploaded_images_and_files:
            file = File(content=content, post_id=post.id)
            db.session.add(file)
            db.session.commit()

        flash('Post created successfully', 'success')

        return redirect(url_for('group_views.group_content', group_id=group_id))

    return render_template('group_content.html', form=form, group=group, user=current_user, posts=posts)
