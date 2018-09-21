#!flask/bin/python
from flask import request, jsonify, Flask, render_template, flash
from geopy.geocoders import Nominatim
from my_power import *
import json

class NotEnoughDataException(Exception):
    pass

app = Flask(__name__, static_url_path='')
app.secret_key = b'\x1c\xd2\xbf\xfc`&x\xf4\xab\x04\xc6\xf3B\x02\x9d]\t\xddP`\x97%\x14\xd4'
app.url_map.strict_slashes = False

geolocator = Nominatim(user_agent="off-grid")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/search/', methods=['POST'])
def get_coordinates():
     location = geolocator.geocode(request.form['search'])
     coordinates = location.latitude, location.longitude
     return jsonify(coordinates)

@app.route('/api/power/', methods=['POST'])
def get_energy():
    print("request: %s" % request.form)
    lat = float(request.form['lat'])
    lng = float(request.form['lng'])
    tz = 'US/Mountain'
    surface_tilt = int(request.form['surface_tilt'])
    surface_azimuth = int(request.form['surface_azimuth'])
    albedo = float(request.form['albedo'])
    panel = Panel(lat, lng, tz, surface_tilt, surface_azimuth, albedo)
    forecast = Forecast(panel=panel)
    coordinates = "'" + request.form['lat'] + ", " + request.form['lng'] + "'"
    location = geolocator.reverse(coordinates)
    print("location: %s" % location.address)
    response = location.address, forecast.get_avg_daily_dc_power()
    return jsonify(response)



if __name__ == '__main__':
    app.run(debug=True)
