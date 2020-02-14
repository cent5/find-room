import json
import logging

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

    @classmethod
    def from_dict(cls, **kwargs):
        proto = {}
        for column in Listing.__table__.columns:
            if column.name in ('id', 'created_at'):
                continue
            if isinstance(column.type, db.String):
                proto[column.name] = kwargs[column.name]
            elif isinstance(column.type, db.Integer):
                proto[column.name] = IntegerValidator(kwargs[column.name]).validated
            elif isinstance(column.type, db.Float):
                proto[column.name] = FloatValidator(kwargs[column.name]).validated
            elif isinstance(column.type, db.DateTime):
                proto[column.name] = DateTimeValidator(kwargs[column.name]).validated
            else:
                assert False
        return cls(**proto)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_json_primitives(self):
        result = {}
        for column in Listing.__table__.columns:
            result[column.name] = str(getattr(self, column.name))
        # result["__type"] = self.__class__.__name__
        return result

    def json(self):
        return json.dumps(self.to_json_primitives())


def get_listings(limit=10):
    return Listing.query.limit(limit).all()


def add_listings(keys, rows):
    listings = []
    failure_cnt = 0
    for values in rows:
        kwargs = {}
        for k, v in zip(keys, values):
            field_name = 'imported_id' if k == 'id' else k
            kwargs[field_name] = v
        try:
            listings.append(Listing.from_dict(**kwargs))
        except ValueError as e:
            logging.error(f'Cannot create Listing object with bad data: {e}')
            failure_cnt += 1
    db.session.add_all(listings)
    db.session.commit()
    return len(listings), failure_cnt
