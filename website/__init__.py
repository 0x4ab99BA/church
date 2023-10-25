from flask import Flask, request, url_for, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_ckeditor import CKEditor, upload_fail, upload_success, CKEditorField
import os
# from flask_wtf.csrf import CSRFProtect
db = SQLAlchemy()
DB_NAME = "database.db"
basedir = os.path.abspath(os.path.dirname(__file__))
ckeditor = CKEditor()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['RECAPTCHA_USE_SSL'] = False
    app.config['RECAPTCHA_PUBLIC_KEY'] = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
    app.config['RECAPTCHA_PRIVATE_KEY'] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'
    app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}
    app.config['CKEDITOR_PKG_TYPE'] = 'full'
    app.config['CKEDITOR_SERVE_LOCAL'] = True
    app.config['CKEDITOR_HEIGHT'] = 400
    app.config['CKEDITOR_FILE_UPLOADER'] = 'views.upload'
    app.config['UPLOADED_PATH'] = os.path.join(basedir, 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
    # app.config['CKEDITOR_ENABLE_CSRF'] = True

    db.init_app(app)
    ckeditor.init_app(app)
    # csrf = CSRFProtect(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note

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
