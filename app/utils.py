"""
Utility functions and constants.
"""

import enum
import logging
from datetime import datetime
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

from flask import jsonify

SEPARATOR = ','
WEIRD_COMMA = '，'

# users can specify the serch diameter, but we enforce a minimum value
MINIMUM_SEARCH_DIAMETER = 1  # km

LISTING_DB_SEARCH_LIMIT = 200  # maximum number of listings when querying DB
LISTING_SEARCH_LIMIT = 100     # maximum number of listings returning to user

# approximate radius of earth
R = 6373.0  # km

def calculate_distance(latA, lonA, latB, lonB):
    latA, lonA, latB, lonB = map(radians, [latA, lonA, latB, lonB])
    lat_delta = latB - latA
    lon_delta = lonB - lonA
    a = sin(lat_delta / 2) ** 2 + cos(latA) * cos(latB) * sin(lon_delta / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


class BaseValidator:
    @property
    def validated(self):
        return self._x


class IntegerValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            x = x.strip('\x00')
            self._x = int(x)

class FloatValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            x = x.strip('\x00')
            self._x = float(x)

class DateTimeValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            x = x.strip('\x00')
            self._x = datetime.strptime(x[:10], '%Y-%m-%d')

class NonBlankStringValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if not x:
            raise ValueError('string should be non-blank')
        self._x = str(x)


class RoomType(str, enum.Enum):
    default = 'default'
    unknown = 'unknown'
    entire = 'entire'
    private = 'private'
    shared = 'shared'

    @staticmethod
    def from_str(room_type):
        reformatted = room_type.lower().replace(' ', '')
        if reformatted == 'privateroom':
            return RoomType.private
        if reformatted == 'sharedroom':
            return RoomType.shared
        if reformatted == 'entirehome/apt':
            return RoomType.entire
        raise ValueError(f"Unrecognized room type: {room_type}")

    @staticmethod
    def guess_from_str(query):
        if 'private' in query:
            return RoomType.private
        if 'shared' in query:
            return RoomType.shared
        if 'entire' in query:
            return RoomType.entire
        return RoomType.unknown

class RoomTypeValidator(BaseValidator):
    def __init__(self, x):
        self._x = RoomType.from_str(x)


def json_error(error_msg):
    return jsonify({'status': 'error',
                    'message': error_msg})


def read_csv(lines):
    unicoded_lines = list(map(lambda x: x.decode('UTF-8').strip(), lines))
    keys = list(map(lambda x: x.lower(), unicoded_lines[0].split(SEPARATOR)))
    results = []
    failure_cnt = 0
    incomplete_row = ''
    for row in unicoded_lines[1:]:
        values = []
        if row.startswith('"') and row.endswith('"'):
            row = row[1:-1]
        row = row.replace(WEIRD_COMMA, SEPARATOR)
        tokens = row.strip().split(SEPARATOR)
        try:
            int(tokens[0])
            if incomplete_row:
                logging.error(f'Cannot import listing [{row}] {len(keys)}!={len(values)}')
                failure_cnt += 1
                incomplete_row = ''
        except ValueError:
            row = incomplete_row + row
            tokens = row.split(SEPARATOR)
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
        if len(keys) == len(values):
            results.append(values)
            incomplete_row = ''
        else:
            if incomplete_row:
                logging.error(f'Cannot import listing [{row}] {len(keys)}!={len(values)}')
                failure_cnt += 1
            incomplete_row = row
    return keys, results, failure_cnt
