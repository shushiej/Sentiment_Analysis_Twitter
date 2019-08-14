import sqlite3
import settings


def create_table():
    conn = sqlite3.connect(settings.SQLALCHEMY_DATABASE_URI)

    c = conn.cursor()

    #c.execute("DROP TABLE tweets;")

    c.execute("""CREATE TABLE IF NOT EXISTS tweets (
                user TEXT,
                user_id INTEGER,
                raw_tweet TEXT,
                tweets TEXT,
                id INTEGER PRIMARY KEY NOT NULL,
                date_created TEXT,
                likes INTEGER,
                retweet_count INTEGER,
                len INTEGER,
                sentiment REAL,
                subjectivity REAL,
                tweet_date TEXT,
                tweet_day_of_week TEXT,
                tweet_hour INTEGER
        )""")


    conn.commit()

    conn.close()

if __name__ == "__main__":
    create_table()