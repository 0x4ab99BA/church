from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from .models import Post
import os

admin_views = Blueprint('admin_views', __name__)
basedir = os.path.abspath(os.path.dirname(__file__))


@admin_views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    return render_template("admin.html", user=current_user)