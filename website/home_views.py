from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
import os

home_views = Blueprint('home_views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))


@home_views.route('/', methods=['GET', 'POST'])
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