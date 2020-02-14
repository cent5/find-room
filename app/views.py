from flask import jsonify
from flask import request
from flask.views import MethodView

from app import models
from app.utils import FloatValidator
from app.utils import NonBlankStringValidator


class RoomSearchApi(MethodView):
    def get(self):
        for key in ('latitude', 'longitude', 'distance', 'query'):
            if key not in request.args:
                return jsonify({'status': 'error', 'description': 'Missing one or more parameters.'})
        try:
            latitude = FloatValidator(request.args['latitude']).validated
            longitude = FloatValidator(request.args['longitude']).validated
            distance = FloatValidator(request.args['distance']).validated
            query = NonBlankStringValidator(request.args['query']).validated
        except ValueError:
            return jsonify({'status': 'error', 'description': 'Invalid parameter(s) format.'})

        listings = models.get_listings(limit=10)
        return jsonify({'status': 'ok', 'results': listings})


