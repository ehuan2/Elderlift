
import os # necessary module to get env variables

class Config:
    # all the next are necessary configurations
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.environ.get('DB_USER')}:{os.environ.get('DB_PASS')}@/{os.environ.get('DB_NAME')}?unix_socket=/cloudsql/{os.environ.get('CLOUD_SQL_CONNECTION_NAME')}"
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')