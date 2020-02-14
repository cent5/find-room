from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    config_objs = {'production': 'app.config.ProdConfig',
                   'development': 'app.config.DevConfig',
                   'test': 'app.config.DevConfig'}
    app.config.from_object(config_objs['development'])

    db.init_app(app)
    migrate.init_app(app, db)

    from app.views import RoomSearchApi
    app.add_url_rule('/b', methods=['GET'], view_func=RoomSearchApi.as_view('roomsearch'))

    return app


