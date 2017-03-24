import os


WTF_CSRF_ENABLED = True
SECRET_KEY = os.environ.get('SECRET_KEY')
SALT_EMAIL_KEY = os.environ.get('SALT_EMAIL_KEY')
SALT_RECOVERY_KEY = os.environ.get('SALT_RECOVERY_KEY')

basedir = os.path.abspath(os.path.dirname(__file__))

ONLINE_LAST_MINUTES = 1                

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SQLALCHEMY_TRACK_MODIFICATIONS = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

UPLOAD_FOLDER = os.path.join(basedir, 'app/static/uploads')
RELATIVE_UPLOAD_FOLDER = '/static/uploads/'
DEFAULT_AVATAR = '/static/uploads/default_av_image.png'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')             
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')             
 
ADMINS = ['aliev.gennadiy@gmail.com']

BCRYPT_LOG_ROUNDS = 10             

POSTS_PER_PAGE = 8
