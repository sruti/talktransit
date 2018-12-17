import fileinput
import json
import gmplot
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError

from collections import Counter
import pprint

def open_tweets(filename):
    tweets = []
    for line in fileinput.FileInput(filename):
        try:
            tweet_dict = json.loads(line)
            tweet = Tweet(tweet_dict)
        except (json.JSONDecodeError,NotATweetError):
            pass
        tweets.append(tweet)
    return tweets


def draw_heatmap(map_center_lat, map_center_long, zoom, plot_coordinates):
    gmap = gmplot.GoogleMapPlotter(map_center_lat, map_center_long, zoom)
    gmap.heatmap(plot_coordinates['latitudes'], plot_coordinates['longitudes'])
    gmap.draw("python_heatmap.html")

def main():
    #Open list of tweets
    tweets = open_tweets("tweet_archive_mtafail.json")
    tweet_coordinates = {
        "latitudes": [tweet.geo_coordinates.get('latitude') for tweet in tweets if tweet.geo_coordinates is not None],
        "longitudes": [tweet.geo_coordinates.get('longitude') for tweet in tweets if tweet.geo_coordinates is not None]
    }

    #Number of tweets with hashtag "#MTAFail"
    print("Number of tweets with #MTAFail: {}".format(len(tweets)))

    #Other hashtags mentioned
    hashtags = [tweet.hashtags for tweet in tweets]
    hashtags_list = [hashtag for hashtag_list in hashtags for hashtag in hashtag_list]
    hashtags_count = Counter(hashtags_list)
    pprint.pprint(hashtags_count)

    #User mentions
    user_mentions = [tweet.user_mentions for tweet in tweets]
    user_mentions_list = [user_mentions.get("screen_name") for user_mentions_list in user_mentions for user_mentions in user_mentions_list]
    user_mentions_count = Counter(user_mentions_list)
    pprint.pprint(user_mentions_count)

    #Plot heatmap
    draw_heatmap(40.7128, -74.0060, 11, tweet_coordinates)


main()