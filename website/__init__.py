import os
from os import path

from flask import Flask
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from dotenv import load_dotenv

db = SQLAlchemy()

DB_NAME = "database.db"
basedir = os.path.abspath(os.path.dirname(__file__))
ckeditor = CKEditor()
load_dotenv()


def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['RECAPTCHA_USE_SSL'] = False
    app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
    app.config['CKEDITOR_PKG_TYPE'] = 'full'
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_HEIGHT'] = 400
    app.config['CKEDITOR_FILE_UPLOADER'] = 'post_views.upload'
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['CKEDITOR_ENABLE_CSRF'] = True

    db.init_app(app)
    ckeditor.init_app(app)

    csp = {
        'default-src': '\'self\'',
        'img-src': ['\'self\'',
                    'data:',
                    'https://cdn.ckeditor.com'],
        'script-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            '\'unsafe-eval\'',
            'maxcdn.bootstrapcdn.com',
            'cdnjs.cloudflare.com',
            'https://code.jquery.com',
            'stackpath.bootstrapcdn.com',
            'www.youtube.com',
            's.ytimg.com',
            'https://www.google.com/recaptcha/',
            'https://www.gstatic.com/recaptcha/',
            'https://cdn.ckeditor.com',
        ],
        'style-src': [
            '\'self\'',
            '\'unsafe-inline\'',
            'maxcdn.bootstrapcdn.com',
            'stackpath.bootstrapcdn.com',
            'https://use.fontawesome.com/releases/v5.15.1/css/all.css',
            'https://cdn.ckeditor.com',
        ],
        'font-src': [
            '\'self\'',
            'maxcdn.bootstrapcdn.com',
            'stackpath.bootstrapcdn.com',
            'use.fontawesome.com'
        ],
        'frame-src': [
            'www.youtube.com',
            'www.youtube-nocookie.com',
            'https://www.google.com/',
        ],
        'connect-src': [
            '\'self\'',
            'cke4.ckeditor.com'
        ]
    }

    Talisman(app, force_https=False, content_security_policy=csp)

    from .auth import auth
    from .home_views import home_views
    from .group_views import group_views
    from .post_views import post_views
    from .admin_views import admin_views

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(home_views, url_prefix='/')
    app.register_blueprint(group_views, url_prefix='/')
    app.register_blueprint(post_views, url_prefix='/')
    app.register_blueprint(admin_views, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
