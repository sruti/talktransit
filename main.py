import fileinput
import json
import pprint
import re
import string

import gmplot
import gensim
from tweet_parser.tweet import Tweet
from tweet_parser.tweet_parser_errors import NotATweetError
from textblob import TextBlob

from collections import Counter


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


def processTweet(tweet):
    # To lowercase
    tweet = tweet.lower()
    # Remove HTML special entities (e.g. &amp;)
    tweet = re.sub(r'\&\w*;', '', tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','',tweet)
    # Remove tickers
    tweet = re.sub(r'\$\w*', '', tweet)
    # Remove hyperlinks
    tweet = re.sub(r'https?:\/\/.*\/\w*', '', tweet)
    # Remove Punctuation and split 's, 't, 've with a space for filter
    tweet = re.sub(r'[' + string.punctuation.replace('@', '') + ']+', ' ', tweet)
    # Remove whitespace (including new line characters)
    tweet = re.sub(r'\s\s+', ' ', tweet)
    # Remove single space remaining at the front of the tweet.
    tweet = tweet.lstrip(' ') 
    # Remove characters beyond Basic Multilingual Plane (BMP) of Unicode:
    tweet = ''.join(c for c in tweet if c <= '\uFFFF') 
    # Bunch st and ave names
    tweet = tweet.replace(' st ', 'st ')
    tweet = tweet.replace(' ave ', 'ave ')

    # Remove stop words
    stoplist = set('for a of the and to in that has on at'.split(' '))
    tweet_tokens = [word for word in tweet.lower().split() if word not in stoplist]

    return tweet_tokens


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
    hashtags_count = Counter(hashtags_list).most_common(5)
    pprint.pprint(hashtags_count)

    #User mentions
    user_mentions = [tweet.user_mentions for tweet in tweets]
    user_mentions_list = [user_mentions.get("screen_name") for user_mentions_list in user_mentions for user_mentions in user_mentions_list]
    user_mentions_count = Counter(user_mentions_list).most_common(5)
    pprint.pprint(user_mentions_count)

    #Plot heatmap
    draw_heatmap(40.7128, -74.0060, 11, tweet_coordinates)

    # Process tweets
    tweet_corpus = [tweet.text for tweet in tweets]
    processed_corpus = [processTweet(tweet) for tweet in tweet_corpus]

    # Word Vector generation
    model = gensim.models.Word2Vec(processed_corpus, min_count=3)
    word_vector = model.wv

    # Streetname word vector similarity
    streetnames = []
    for tweet in processed_corpus:
        for word in tweet:
            if ('ave' in word or 'st' in word) and bool(re.search(r'\d', word)):
                streetnames.append(word)
    pprint.pprint(Counter(streetnames).most_common(10))

    for streetname in Counter(streetnames).most_common(10):
        print("Word vector for {}".format(streetname))
        try:
            similar_words = word_vector.similar_by_word(streetname)
        except KeyError:
            pass
        pprint.pprint(similar_words)

    # Noun phrase analysis
    tweets_noun_phrases = []
    for tweet in processed_corpus:
        noun_phrases = TextBlob(' '.join(tweet)).noun_phrases
        for phrase in noun_phrases:
            tweets_noun_phrases.append(phrase)
    
    pprint.pprint(Counter(tweets_noun_phrases).most_common(10))

main()