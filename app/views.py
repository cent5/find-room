from flask import jsonify
from flask import request
from flask.views import MethodView

from app import models
from app.utils import FloatValidator
from app.utils import LISTING_SEARCH_LIMIT
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

        query = query.lower()
        listings_with_distance = models.filter_listings(latitude, longitude, distance)
        sorted_listings = models.filter_listings_by_query(listings_with_distance, query)
        return jsonify({'status': 'ok', 'results': sorted_listings})


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


class DemoPage(MethodView):
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

        query = query.lower()
        listings_with_distance = models.filter_listings(latitude, longitude, distance)
        sorted_listings = models.filter_listings_by_query(listings_with_distance, query)[:LISTING_SEARCH_LIMIT]

        map_listing_data = [['Lat', 'Long', 'Name']]
        map_listing_data.extend(
            [[x['latitude'], x['longitude'], '\n'.join([x['name'], str(x['price']), str(x['match_score'])])]
             for x in sorted_listings])

        return f'''
        <html>
          <head>
            <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
            <script type="text/javascript">
              google.charts.load("current", {{
                "packages":["map"],
                "mapsApiKey": "AIzaSyD-9tSrke72PouQMnMX-a7eZSW0jkFMBWY"
            }});
              google.charts.setOnLoadCallback(drawChart);
              function drawChart() {{
                var data = google.visualization.arrayToDataTable({str(map_listing_data)});

                var map = new google.visualization.Map(document.getElementById('map_div'));
                map.draw(data, {{
                  showTooltip: true,
                  showInfoWindow: true
                }});
              }}
            </script>
          </head>
          <body>
            <div id="map_div" style="width: 800px; height: 600px"></div>
          </body>
        </html>
        '''
