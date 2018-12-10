import fileinput
import json
import gmplot
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError

tweet_lats = []
tweet_longs = []

for line in fileinput.FileInput("tweet_archive.json"):
    try:
        tweet_dict = json.loads(line)
        tweet = Tweet(tweet_dict)
    except (json.JSONDecodeError,NotATweetError):
        pass
    if tweet.geo_coordinates is not None:
        tweet_lats.append(tweet.geo_coordinates.get('latitude'))
        tweet_longs.append(tweet.geo_coordinates.get('longitude'))


gmap = gmplot.GoogleMapPlotter(40.7128, -74.0060, 11)
gmap.heatmap(tweet_lats, tweet_longs)
gmap.draw("python_heatmap.html")