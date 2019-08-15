from app import db 

class Tweets(db.Model):

    __tablename__ = "tweeter"

    user = db.Column(db.String, nullable = False)
    user_id = db.Column(db.Integer, nullable = False)
    raw_tweet = db.Column(db.String)
    tweets = db.Column(db.String)
    id = db.Column(db.Integer, primary_key = True)
    date_created = db.Column(db.String, nullable = False)
    likes = db.Column(db.Integer)
    retweet_count = db.Column(db.Integer)
    len = db.Column(db.Integer)
    sentiment = db.Column(db.Numeric(10,2))
    subjectivity = db.Column(db.Numeric(10,2))
    tweet_date = db.Column(db.String)
    tweet_day_of_week = db.Column(db.String)
    tweet_hour = db.Column(db.Integer)

    def __init__(self, user, user_id, raw_tweet, tweets, id, date_created,
                    likes, retweet_count, len, sentiment, subjectivity, tweet_date, 
                    tweet_day_of_week, tweet_hour):
        self.user = user
        self.user_id = user_id
        self.raw_tweet = raw_tweet
        self.tweets = tweets
        self.id = id
        self.date_created = date_created
        self.likes = likes
        self.retweet_count = retweet_count
        self.len = len
        self.sentiment = sentiment
        self.subjectivity = subjectivity
        self.tweet_date = tweet_date
        self.tweet_day_of_week = tweet_day_of_week
        self.tweet_hour = tweet_hour

    def __repr__(self):
        return '{} {} {} {} {} {} {} {} {} {} {} {} {} {}'.format(self.user, self.user_id, self.raw_tweet, self.tweets, self.id, self.date_created, self.likes, self.retweet_count, self.len, self.sentiment, self.subjectivity, self.tweet_date, self.tweet_day_of_week, self.tweet_hour)

if __name__ == "__main__":
    tweets = Tweets.query.all()
    print(tweets)