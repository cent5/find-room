from datetime import datetime

from flask import jsonify

SEPARATOR = ','


class BaseValidator:
    @property
    def validated(self):
        return self._x


class IntegerValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            self._x = int(x)

class FloatValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            self._x = float(x)

class DateTimeValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if x:
            self._x = datetime.strptime(x[:10], '%Y-%m-%d')

class NonBlankStringValidator(BaseValidator):
    def __init__(self, x):
        self._x = None
        if not x:
            raise ValueError('string should be non-blank')
        self._x = str(x)


def json_error(error_msg):
    return jsonify({'status': 'error',
                    'message': error_msg})


def read_csv(lines):
    unicoded_lines = list(map(lambda x: x.decode('UTF-8').strip(), lines))
    keys = list(map(lambda x: x.lower(), unicoded_lines[0].split(SEPARATOR)))
    results = []
    failure_cnt = 0
    for irow, row in enumerate(unicoded_lines[1:]):
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
        if len(keys) == len(values):
            results.append(values)
        else:
            failure_cnt += 1
    return keys, results, failure_cnt