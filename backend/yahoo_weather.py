from weather import Weather, Unit
from datetime import datetime, timedelta

weather = Weather(unit=Unit.CELSIUS)

def convert_str_to_time(time):
    return datetime.strptime(time, '%I:%M %p')

def get_sunlight_minutes(location):
    sunset = convert_str_to_time(location.astronomy['sunset'])
    sunrise = convert_str_to_time(location.astronomy['sunrise'])
    print("sunset: %s" % sunset)
    print("sunrise: %s" % sunrise)
    sun_time = sunset - sunrise
    return timedelta.total_seconds(sun_time) / 60

# https://docs.python.org/3/library/datetime.html
# https://anthonybloomer.github.io/weather-api/
# https://developer.yahoo.com/weather/documentation.html?guccounter=1
