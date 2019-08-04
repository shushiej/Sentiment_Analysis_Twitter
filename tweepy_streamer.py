from tweepy import API, Cursor, OAuthHandler, Stream
from tweepy.streaming import StreamListener
import creds
import json

class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenicator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets
    
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
        auth = OAuthHandler(creds.CONSUMER_API_KEY, creds.CONSUMER_SECRET)
        auth.set_access_token(creds.ACCESS_TOKEN, creds.ACCESS_TOKEN_SECRET)
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


if __name__ == '__main__':
    hashtag_list = ['Fed rate cut'] # This needs to be populated by Google Trends.
    fname  = 'tweets.json'
    twitter_client = TwitterClient("pycon")

    #ts = TwitterStreamer()
    #ts.stream_tweets(fname, hashtag_list)