from flask_sqlalchemy import SQLAlchemy

from app import db
from app.utils import DateTimeValidator
from app.utils import FloatValidator
from app.utils import IntegerValidator


class Listing(db.Model):
    __tablename__ = 'listing'
    id = db.Column(db.Integer, primary_key=True)
    # created_at = db.Column(DateTime)
    # imported_src = db.Column(db.String)  # notes about source, e.g. filename
    imported_id = db.Column(db.Integer)
    name = db.Column(db.String)
    host_id = db.Column(db.Integer)
    host_name = db.Column(db.String)
    neighbourhood_group = db.Column(db.String)
    neighbourhood = db.Column(db.String)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    room_type = db.Column(db.String)
    price = db.Column(db.Float)  # USD
    minimum_nights = db.Column(db.Integer)
    number_of_reviews = db.Column(db.Integer)
    last_review = db.Column(db.DateTime)
    reviews_per_month = db.Column(db.Float)
    calculated_host_listings_count = db.Column(db.Integer)
    availability_365 = db.Column(db.Integer)

    def __init__(self, **kwargs):
        #assert len(keys) == len(values), "do not call this function with blatantly bad data"
        #if str(Listing.name.property.db.Columns[0].type) == 'VARCHAR':
        obj = {}
        for column in Listing.__table__.columns:
            if column.name in ('id', 'created_at'):
                continue
            if isinstance(column.type, db.String):
                obj[column.name] = kwargs[column.name]
            elif isinstance(db.Column.type, db.Integer):
                obj[column.name] = IntegerValidator(kwargs[column.name]).validated
            elif isinstance(db.Column.type, db.Float):
                obj[column.name] = FloatValidator(kwargs[column.name]).validated
            elif isinstance(db.Column.type, db.DateTime):
                obj[column.name] = DateTimeValidator(kwargs[column.name]).validated
            else:
                assert False
        self.__dict__.update(obj)


def get_listings(limit=10):
    return Listing.query.limit(limit).all()


