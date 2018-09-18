import urllib2, urllib, json

# yahoo_app_id = "yEaDfC4g"
# yahoo_consumer_key = "dj0yJmk9MTNOZTgxQlNnQ0ZrJmQ9WVdrOWVVVmhSR1pETkdjbWNHbzlNQS0tJnM9Y29uc3VtZXJzZWNyZXQmeD04Mw--"
# yahoo_secret = "3dffcf52d6b745a098daa6d3f15c0208e62b170c"

baseurl = "https://query.yahooapis.com/v1/public/yql?"
yql_query = "select wind from weather.forecast where woeid=2460286"
yql_url = baseurl + urllib.urlencode({'q':yql_query}) + "&format=json"
result = urllib2.urlopen(yql_url).read()
data = json.loads(result)
print data['query']['results']
