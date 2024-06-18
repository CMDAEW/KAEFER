from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import os
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    Bootstrap(app)

    # Load configuration from config file
    app.config.from_object('config.Config')

    # Set the database URI dynamically
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flaskuser:flaskpassword@localhost/invoicing'
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from .models import User  # Import the User model

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Apply ProxyFix middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Ensure all tables are created
    with app.app_context():
        db.create_all()



    return app

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    },
    'loggers': {
        'sqlalchemy.engine': {
            'level': 'WARN',
            'handlers': ['wsgi'],
            'propagate': False,
        },
        'sqlalchemy.pool': {
            'level': 'WARN',
            'handlers': ['wsgi'],
            'propagate': False,
        },
        'sqlalchemy.dialects': {
            'level': 'WARN',
            'handlers': ['wsgi'],
            'propagate': False,
        }
    }
})

def setup_logging():
    handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)