#!flask/bin/python
from flask import request, jsonify, Flask, render_template, flash
# from yahoo_weather import data
from my_power import *
import json

class NotEnoughDataException(Exception):
    pass

app = Flask(__name__, static_url_path='')
app.secret_key = b'\x1c\xd2\xbf\xfc`&x\xf4\xab\x04\xc6\xf3B\x02\x9d]\t\xddP`\x97%\x14\xd4'
app.url_map.strict_slashes = False

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/power/', methods=['POST'])
def get_energy():
    print(request.form)
    return request.form['lng']

    # return json.dumps({'status':'OK','lng':request.form['lng'],'lat':request.form['lat']});

# @app.route('/yahoo/', methods=['GET'])
# def yahoo_test():
#     return jsonify(data)

@app.route('/power/', methods=['GET'])
def power_test():
    forecast = Forecast()
    return forecast.get_avg_daily_dc_power()

def format_coordinates(args):
    longitude = None
    latitude = None
    if 'longitude' in args:
        longitude = args['longitude']
    else:
        raise NotEnoughDataException("No longitude presented!")
    if 'latitude' in args:
        latitude = args['latitude']
    else:
        raise NotEnoughDataException("No latitude presented!")
    return longitude, latitude

def get_sunlight_hours():
    return

def get_wind_speed():
    return

def calculate_energy_sulight():
    return

def calculate_energy_wind_speed():
    return


if __name__ == '__main__':
    app.run(debug=True)
