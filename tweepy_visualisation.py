import dash 
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.graph_objs as go
import pandas as pd 
import numpy as np
import base64
import sqlite3

# Get Twitter User from DB and convert to Dataframe.
conn = sqlite3.connect('tweets.db')
cur = conn.cursor()
cur.execute("SELECT * FROM tweets where user = 'TheNotoriousMMA'")
rows = cur.fetchall()
df = pd.DataFrame(rows, columns=['user', 'user_id', 'tweets', 'id', 'date_created', 'likes', 'retweet_count', 'len', 'sentiment','subjectivity', 'tweet_date', 'tweet_day_of_week', 'tweet_hour'])
conn.commit()
conn.close()

# Process the CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Manipulate DF for extra information.
tweet_counts_by_week = pd.DataFrame(df.groupby(df['tweet_day_of_week'])['tweets'].count())

bins = [0, 3, 6, 9, 12, 15, 18, 21, 23]
df_2 = pd.DataFrame(df.groupby(pd.cut(df['tweet_hour'], bins=bins, labels=['0-3am', '3-6am', '6-9am', '9-12pm', '12-3pm', '3-6pm', '6-9pm', '9-11pm'])).tweets.count())
df_2.reset_index(level=0, inplace=True)

max_idx = df.groupby(['tweets'])['likes'].transform(max) == df['likes'].max()
df['most_liked_tweet']= df[max_idx]['tweets'][:1]

min_idx = df.groupby(['tweets'])['likes'].transform(max) == df['likes'].min()
df['least_liked_tweet'] = df[min_idx]['tweets'][:1]

most_retweets_idx = df.groupby(['tweets'])['retweet_count'].transform(max) == df['retweet_count'].max()
df['most_retweeted_tweet'] = df[most_retweets_idx]['tweets'][:1]

# Get image of Wordcloud.
DASH_APP = "Sentiment_Analysis_Twitter"
STATIC_PREFIX = '/{}/data/img/'.format(DASH_APP)
image_filename = './data/img/elonmusk.png'
encoded_img = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div(children = [
    html.H1(children = '@'+df['user'][0]),
    html.Img(src='/data/img/elonmusk.png', style={'height': '50%'}),
    html.H5(children='Most Liked Tweet'),
    html.P(children = df['most_liked_tweet']),
    html.H5(children='Least Liked Tweet'),
    html.P(children = df['least_liked_tweet']),
    html.H5(children='Most retweeted Tweet'),
    html.P(children = df['most_retweeted_tweet']),
    html.H3(children= 'Tweet Metrics'),
    html.Div(children = [
        html.Div(children = [
            dcc.Graph(
        id='num_likes',
        figure={
            'data': [
                go.Bar(
                    x=df['tweet_day_of_week'],
                    y=df['likes'],
                    opacity=0.9,
                    name='Num Likes'
                ),
                go.Bar(
                    x=df['tweet_day_of_week'],
                    y=df['retweet_count'],
                    opacity=0.9,
                    name='Num Retweets'
                )
            ],
            'layout': go.Layout(
                hovermode='closest',
                title='Likes vs Retweets'
            )
        }
        ),
    ],className = 'six columns'), 
    html.Div(children = [
                dcc.Graph(
        id='num_tweets',
        figure={
            'data': [
                go.Bar(
                    x=tweet_counts_by_week.index,
                    y=tweet_counts_by_week['tweets'],
                    text='Tweets per Day',
                    opacity=0.6
                )
            ],
            'layout': go.Layout(
                hovermode='closest',
                title='Tweets per Week'
            )
        }
    ),
    ], className = 'six columns'),
    ]),
    html.Div(children = [
        html.Div(children = [
            html.Div(children = [
                dcc.Graph(
                    id='num_tweets_by_hour',
                    figure={
                        'data': [
                            go.Bar(
                                x=df_2['tweet_hour'],
                                y=df_2['tweets'],
                                text='Tweets per Hour',
                                opacity=0.6
                            )
                        ],
                'layout': go.Layout(
                    hovermode='closest',
                    title='Tweets per Hour'
                )
            }
    ),
        ], className = 'six columns'),
        ], className = "offset-by-one")
    ], className = "ten columns offset-by-one"),
    html.H3(children= 'Tweet Content Analysis', className = 'twelve columns'),
    html.Div(children = [
        html.Div(children = [
             dcc.Slider(
                id='sentiment_polarity',
                min = -1,
                max = 1,
                marks = {
                    -1: {'label': 'Very Negative', 'style' : {'color' : '#ce2939'}},
                    -0.5: 'Slightly Negative',
                    0: 'Neutral',
                    0.5: 'Slightly Positive',
                    1: {'label': 'Very Positive', 'style' : {'color' : '#1876fb'}}
                },
                value = df['sentiment'].mean(),
                step = 0.2,
                included=False
        ),
        ], className = 'six columns'),
        html.Div(children = [
            dcc.Slider(
                id='subjectivity',
                min = -1,
                max = 1,
                marks = {
                    -1: 'Very Subjective',
                    -0.5: 'Slightly Subjective',
                    0: 'Neutral',
                    0.5: 'Slightly Objective',
                    1: 'Very Objective'
                },
                value = df['subjectivity'].mean(),
                step = 0.2,
                included=False
            )
        ], className = 'six columns') 
    ], className = 'offset-by-one')
    

])


if __name__ == '__main__':
    app.run_server(debug=True)