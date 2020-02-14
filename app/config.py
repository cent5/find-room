class BaseConfig:
    DEBUG = False
    TESTING = False

    # SQLAlchemy (http://pythonhosted.org/Flask-SQLAlchemy/)
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/roomapi.db'


class DevConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False