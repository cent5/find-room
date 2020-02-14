from datetime import datetime


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
