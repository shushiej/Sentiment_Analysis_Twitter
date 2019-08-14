from tweepy import API, Cursor, OAuthHandler, Stream
from tweepy.streaming import StreamListener
import settings
import json
import sys
import re
import sqlite3
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
import os

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenicator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user
       
        self.tweets = []
        
    
    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            self.tweets.append(tweet)
        return self.tweets
        
    
    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_woeid_of_trending_tweets(self):
        with open('woeid_trends.json', 'a') as tf:
            json.dump(self.twitter_client.trends_available(), tf)
    


class TwitterAuthenicator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(settings.CONSUMER_API_KEY, settings.CONSUMER_SECRET)
        auth.set_access_token(settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)
        return auth

class TwitterStreamer():
    def __init__(self):
        self.twiiter_authenicator = TwitterAuthenicator()

    def stream_tweets(self, fname, hashtag_list):
        listener = StdOutListener(fname)
        auth = self.twiiter_authenicator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hashtag_list)
        
class StdOutListener(StreamListener):

    def __init__(self, fname):
        self.fname = fname

    def on_data(self, data):
        try:

            print(data)
            with open(fname, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("error on data %s", str(e))

        return True

    def on_error(self, status):
        if status == 420:
            # Return false if we reach rate limit
            return False
        print(status)

        
        
class TweetAnalyzer():
    
    def __init__(self, name):
        self.twitter_client = TwitterClient()
        self.api = self.twitter_client.get_twitter_client_api()
        self.name = name
    
    def clean_tweet(self, tweet):
        # remove speical characters and hyperlinks
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity
    
    def analyze_subjectivity(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.subjectivity
    
    def user_feed_to_database(self):
        tweets = self.api.user_timeline(screen_name=self.name, count=200, tweet_mode="extended")
        df = self.analyse_tweets(tweets)
        self.tweets_to_db(tweets, df)
    
    def tweets_to_df(self,tweets):
        df = pd.DataFrame(data=[self.clean_tweet(tweet.full_text) for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.id for tweet in tweets])
        df['date_created'] = np.array([tweet.created_at for tweet in tweets])
        df['date_created'] = pd.to_datetime(df['date_created'])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweet_count'] = np.array([tweet.retweet_count for tweet in tweets])
        df['len'] = np.array([len(tweet.full_text) for tweet in tweets])
        df['sentiment'] = np.array([self.analyze_sentiment(tweet) for tweet in df['tweets']])
        df['subjectivity'] = np.array([self.analyze_subjectivity(tweet) for tweet in df['tweets']])
        df['tweet_date'] = [d.date() for d in df['date_created']]
        df['tweet_day_of_week'] = df['date_created'].dt.weekday_name
        df['tweet_hour'] = df['date_created'].dt.hour
        df = df[~df.tweets.str.contains("RT")]
        return df
    
    def tweets_to_db(self, tweets, df):
        print(os.environ.get('server'))
        conn = sqlite3.connect(settings.SQLALCHEMY_DATABASE_URI)
        cur = conn.cursor()
        cur.execute("SELECT id from tweets")
        rows = cur.fetchall()
        for idx, row in df.iterrows():
            if(any(row['id'] in i for i in rows)):
                cur.execute("""UPDATE tweets SET likes = ?, retweet_count = ? WHERE id = ?""",(row['likes'], row['retweet_count'], row['id']) )
            else:
                cur.execute(""" INSERT OR IGNORE INTO 
                        tweets(user, user_id, tweets, id, date_created, likes, retweet_count, len, sentiment, subjectivity, tweet_date, tweet_day_of_week, tweet_hour)
                        values(?,?,?,?,?,?,?,?,?,?,?,?,?)""", (tweets[0].user.screen_name , tweets[0].id, row['tweets'], row['id'], row['date_created'].strftime("%d-%b-%Y (%H:%M:%S.%f)"), row['likes'], row['retweet_count'],  row['len'], row['sentiment'], row['subjectivity'], row['tweet_date'], row['tweet_day_of_week'], row['tweet_hour']))
        
        conn.commit()
        conn.close()
        
    
    def analyse_tweets(self, tweets):
        df = self.tweets_to_df(tweets)
        df['av_len_tweet'] = np.mean(df['len'])
        df['av_tweets_per_day'] = df.groupby('tweet_date')['tweets'].count().mean() 
        df['av_sentiment'] = np.mean(df['sentiment'])
        df['av_subjectivity'] = np.mean(df['subjectivity'])
        
        max_idx = df.groupby(['tweets'])['likes'].transform(max) == df['likes'].max()
        df['most_liked_tweet']= df[max_idx]['tweets'][:1]
        
        min_idx = df.groupby(['tweets'])['likes'].transform(max) == df['likes'].min()
        df['least_liked_tweet'] = df[min_idx]['tweets'][:1]
        
        most_retweets_idx = df.groupby(['tweets'])['retweet_count'].transform(max) == df['retweet_count'].max()
        df['most_retweeted_tweet'] = df[most_retweets_idx]['tweets'][:1]
        return df


if __name__ == '__main__':
    users = ['elonmusk', 'neiltyson', 'rickygervais', 'realDonaldTrump', 'TheNotoriousMMA']
    for user in users:
        ta = TweetAnalyzer(user).user_feed_to_database()