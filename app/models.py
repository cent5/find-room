import json
import logging
from math import cos

from sqlalchemy import func

from app import db
from app.utils import DateTimeValidator
from app.utils import FloatValidator
from app.utils import IntegerValidator
from app.utils import LISTING_DB_SEARCH_LIMIT
from app.utils import MINIMUM_SEARCH_DIAMETER
from app.utils import RoomType
from app.utils import RoomTypeValidator
from app.utils import calculate_distance


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
    room_type = db.Column(db.Enum(RoomType))
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
            if column.name == 'room_type':
                proto[column.name] = RoomTypeValidator(kwargs[column.name]).validated
            elif isinstance(column.type, db.String):
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

    def to_dict(self):
        result = {}
        for column in Listing.__table__.columns:
            result[column.name] = getattr(self, column.name)
        # result["__type"] = self.__class__.__name__
        return result

    def json(self):
        return json.dumps(self.to_dict())


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


def get_listings(limit=10):
    return Listing.query.limit(limit).all()


def filter_listings(latitude, longitude, distance):
    # todo: figure if distance is in the correct units (km); if not, convert
    distance = min(MINIMUM_SEARCH_DIAMETER, distance)
    # approximate the max and min lat/lon giving the center point of search
    lat_threshold = distance / 111.111
    lon_threshold = abs(distance / 111.111 / cos(latitude))
    listings = Listing.query.filter(
        func.abs(Listing.latitude - latitude) <= lat_threshold,
        func.abs(Listing.longitude - longitude) <= lon_threshold).limit(LISTING_DB_SEARCH_LIMIT).all()
    results = []
    for listing in listings:
        calculated_distance = calculate_distance(
            listing.latitude, listing.longitude, latitude, longitude)
        if calculated_distance > distance:
            continue
        result_item = listing.to_dict()
        result_item['distance'] = calculated_distance
        results.append(result_item)
    return results


def calculate_score(listing, query):
    query = query.strip().lower()
    score = 0
    guessed_room_type = RoomType.guess_from_str(query)
    if guessed_room_type != RoomType.unknown and listing['room_type'] == guessed_room_type:
        score += 2
    if listing['neighbourhood_group'].lower() in query:
        score += 1
    if listing['neighbourhood'].lower() in query:
        score += 1
    for token in query.split(' '):
        if token in listing['host_name'].lower():
            score += 1
        if token in listing['name'].lower():
            score += 1
    return score


def filter_listings_by_query(listings, query):
    """Loosely match the input query against our listings.

    Aim to be as useful to the user as possible.
    """
    results = []
    for listing in listings:
        item = listing
        item['match_score'] = calculate_score(listing, query)
        results.append(item)
    return sorted(results, key=lambda x: x['match_score'], reverse=True)

