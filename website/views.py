import json
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Group, Note, GroupForm, PostForm, Post, User


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    subscribed_groups = current_user.subscriptions

    if current_user.is_authenticated:
        # 查询当前用户订阅的群组
        user = User.query.get(current_user.id)
        subscribed_groups = user.subscriptions

        # 查询每个群组的最新帖子
        latest_posts = []
        for group in subscribed_groups:
            latest_post = Post.query.filter_by(group_id=group.id).order_by(Post.created_at.desc()).first()
            if latest_post:
                latest_posts.append(latest_post)

        return render_template('home.html',
                               latest_posts=latest_posts,
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
        content = form.content.data
        post = Post(title=title, content=content, user_id=current_user.id, group_id=group_id)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('views.group_content', group_id=group_id))

    return render_template('group_content.html', form=form, group=group, user=current_user, posts=posts)
