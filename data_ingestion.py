import re

import sqlalchemy

from app.models import Listing

INPUT_FILE = 'data/AB_NYC_2019.csv'
SEPARATOR = ',' #，'


VALIDATOR = {
    'id': lambda x: x.isdigit(),
    'host_id': lambda x: x.isdigit(),
    'minimum_nights': lambda x: x.isdigit(),
    'number_of_reviews': lambda x: x.isdigit(),
    'calculated_host_listings_count': lambda x: x.isdigit(),
    'availability_365': lambda x: x.isdigit(),

    'latitude': lambda x: bool(re.fullmatch(r'\d+\.\d+', x)),
    'longitude': lambda x: bool(re.fullmatch(r'[+-]\d+\.\d+', x)),
    #'reviews_per_month': lambda x: bool(re.fullmatch(r'\d+\.\d+', x)),
    'price': lambda x: bool(re.fullmatch(r'\d+\.?\d+', x)),
}


def numerical_id_validator(x):
    if not x.isdigit():
        return None
    return int(x)


def is_valid(keys, values):
    if len(keys) != len(values):
        # print('len error:', values)
        return False
    for k, v in zip(keys, values):
        if k in VALIDATOR and not VALIDATOR[k](v):
            # print('error:', k, v)
            return False
    return True


def read_csv(filename):
    with open(INPUT_FILE, 'r') as fin:
        headers = fin.readline().strip()
        rows = fin.readlines()
    keys = list(map(lambda x: x.lower(), headers.split(SEPARATOR)))
    print(keys)
    rooms = []
    for irow, row in enumerate(rows):
        values = []
        tokens = row.strip().split(SEPARATOR)
        i = 0
        grouping_cnt = 0
        while i < len(tokens):
            if tokens[i].startswith('"') and not tokens[i].endswith('"'):
                grouping_cnt = 1
            elif tokens[i].endswith('"'):
                values.append(SEPARATOR.join(tokens[i - grouping_cnt + 1:i + 1]))
                grouping_cnt = 0
            elif grouping_cnt:
                grouping_cnt += 1
            else:
                values.append(tokens[i])
            i += 1
        if is_valid(keys, values):
            rooms.append(values)
        else:
            # print('PARSE ERROR:', row)
            pass
    return keys, rooms




def init_db(listings):
    engine = sqlalchemy.create_engine('sqlite:///db.sqlite3', echo=True)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    session = Session()
    session.add_all(listings)
    session.commit()



keys, data = read_csv(INPUT_FILE)
listings = []
for values in data:
    kwargs = {}
    for k, v in zip(keys, values):
        field_name = 'imported_id' if k == 'id' else k
        kwargs[field_name] = v
    listings.append(Listing(**kwargs))
init_db(listings)