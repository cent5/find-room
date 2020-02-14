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
    from app.views import UploadListingData
    from app.views import RoomListApi
    app.add_url_rule('/searchRoom', methods=['GET'], view_func=RoomSearchApi.as_view('searchRoom'))
    app.add_url_rule('/uploadData', methods=['GET', 'POST'], view_func=UploadListingData.as_view('uploadData'))
    app.add_url_rule('/listRoom', methods=['GET'], view_func=RoomListApi.as_view('listRoom'))

    return app


