from flask import jsonify
from flask import request
from flask.views import MethodView

from app import models
from app.utils import FloatValidator
from app.utils import NonBlankStringValidator
from app.utils import json_error
from app.utils import read_csv


class RoomSearchApi(MethodView):
    def get(self):
        for key in ('latitude', 'longitude', 'distance', 'query'):
            if key not in request.args:
                return json_error('Missing one or more parameters')
        try:
            latitude = FloatValidator(request.args['latitude']).validated
            longitude = FloatValidator(request.args['longitude']).validated
            distance = FloatValidator(request.args['distance']).validated
            query = NonBlankStringValidator(request.args['query']).validated
        except ValueError:
            return jsonify('Invalid parameter(s) format')

        listings = models.get_listings(limit=10)
        return jsonify({'status': 'ok', 'results': [x.json() for x in listings]})


class UploadListingData(MethodView):
    def get(self):
        return '''
        <!doctype html>
        <title>Upload Listing Data CSV File</title>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
        '''

    def post(self):
        if 'file' not in request.files:
            return json_error('No file part')
        file = request.files['file']
        if not file.filename:
            return json_error('No selected file')
        lines = file.readlines()
        keys, rows, csv_failures = read_csv(lines)
        added, object_creation_failures = models.add_listings(keys, rows)
        return jsonify({
            'status': 'ok',
            'message': f'Added {added} records, '
                       f'failed with {csv_failures + object_creation_failures} other records(s)'})
