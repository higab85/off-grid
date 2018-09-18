#!flask/bin/python
from flask import request, Flask
# from yahoo_weather import data

class NotEnoughDataException(Exception):
    pass

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello, World!"


@app.route('/api/energy/', methods=['GET'])
def get_energy():
    format_coordinates(request.args)
    return ""


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
