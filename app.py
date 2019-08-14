import dash 
import dash_core_components as dcc 
import dash_html_components as html 
import plotly.graph_objs as go
import pandas as pd 
import numpy as np
import base64
import sqlite3
import tweepy_streamer
import settings
import tweepy_db
# Process the CSS
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def generate_dataframe(name):
    tweepy_db.create_table()
    # Get Twitter User from DB and convert to Dataframe.
    conn = sqlite3.connect(settings.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tweets where user = ?", (name, ))
    rows = cur.fetchall()
    df = pd.DataFrame(rows, columns=['user', 'user_id', 'raw_tweet', 'tweets', 'id', 'date_created', 'likes', 'retweet_count', 'len', 'sentiment','subjectivity', 'tweet_date', 'tweet_day_of_week', 'tweet_hour'])
    conn.commit()
    conn.close()

    tweet_counts_by_week = pd.DataFrame(df.groupby(df['tweet_day_of_week'])['tweets'].count())

    bins = [0, 3, 6, 9, 12, 15, 18, 21, 23]
    df_2 = pd.DataFrame(df.groupby(pd.cut(df['tweet_hour'], bins=bins, labels=['0-3am', '3-6am', '6-9am', '9-12pm', '12-3pm', '3-6pm', '6-9pm', '9-11pm'])).tweets.count())
    df_2.reset_index(level=0, inplace=True)

    max_idx = df.groupby(['raw_tweet'])['likes'].transform(max) == df['likes'].max()
    df['most_liked_tweet']= df[max_idx]['raw_tweet'][:1]

    min_idx = df.groupby(['raw_tweet'])['likes'].transform(max) == df['likes'].min()
    df['least_liked_tweet'] = df[min_idx]['raw_tweet'][:1]

    most_retweets_idx = df.groupby(['raw_tweet'])['retweet_count'].transform(max) == df['retweet_count'].max()
    df['most_retweeted_tweet'] = df[most_retweets_idx]['raw_tweet'][:1]

    return df, df_2, tweet_counts_by_week


app.layout = html.Div(children = [
    html.Div(className="dropdown_container twelve columns", children =[
        dcc.Dropdown(
            id='twitter_user',
            options = [
                {'label' : 'Elon Musk', 'value' : 'elonmusk'},
                {'label' : 'Donald Trump', 'value' : 'realDonaldTrump'},
                {'label' : 'Neil DeGrasse Tyson', 'value' : 'neiltyson'},
                {'label' : 'Conor McGregor', 'value' : 'TheNotoriousMMA'}
            ],
            value='elonmusk'
        ),
        html.Div(id="output_container")
    ]),
], className = 'offset-by-one')

@app.callback(
    dash.dependencies.Output('output_container', 'children'),
    [dash.dependencies.Input('twitter_user', 'value')]
)

def update_output(value):
    if value == None:
        return (html.H1(children = 'Twitter Analysis, Please select a Twitter User above.'))

    df, df_2, tweet_counts_by_week = generate_dataframe(value)

    return (
        html.H1(children = 'Twitter Analysis: @'+df['user'][0]),
        html.Div(className="tweet_storm twelve columns", children = [
        
            html.Blockquote(className = "twitter-tweet", children = [
                html.H3(children='Most Liked Tweet'),
                html.H3(className = "twitter-tweet--handle", children='@'+df['user'][0]),
                html.P(children=df['most_liked_tweet'])
            ]),
            
            html.Blockquote(className = "twitter-tweet", children = [
                html.H3(children='Least Liked Tweet'),
                html.H3(className = "twitter-tweet--handle", children='@'+df['user'][0]),
                html.P(children=df['least_liked_tweet'])
            ]),
           
            html.Blockquote(className = "twitter-tweet", children = [
                html.H3(children='Most retweeted Tweet'),
                html.H3(className = "twitter-tweet--handle", children='@'+df['user'][0]),
                html.P(children=df['most_retweeted_tweet'])
            ])
        ]),
        html.Div(className = "twelve columns", children = [
            html.Div(children = [
                dcc.Graph(
                    id='num_likes',
                    figure={
                        'data': [
                            go.Bar(
                                x=df['tweet_day_of_week'],
                                y=df['likes'],
                                marker = {
                                    'color': '#1DA1F2'
                                },
                                name='Num Likes'
                            ),
                            go.Bar(
                                x=df['tweet_day_of_week'],
                                y=df['retweet_count'],
                                marker = {
                                    'color': '#F7A52D'
                                },
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
                                    text='Tweets per Week',
                                    marker = {
                                        'color': '#1DA1F2'
                                    }
                                )
                            ],
                            'layout': go.Layout(
                                hovermode='closest',
                                title='Tweets per Week'
                            )
                        }
                    ),
            ],className = 'six columns'),
    
        ]),
        html.Div(children = [
            dcc.Graph(
                id='num_tweets_by_hour',
                figure={
                    'data': [
                            go.Bar(
                                x=df_2['tweet_hour'],
                                y=df_2['tweets'],
                                text='Tweets per Hour',
                                marker = {
                                    'color': '#1DA1F2'
                                }
                            )],
                            'layout': go.Layout(
                                hovermode='closest',
                                title='Tweets per Hour'
                            )
                }
            ),
        ], className = "six columns no_margin--left"),
        html.Div(children = [
            html.H3(children= 'Tweet Content Analysis'),
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
        ], className = 'sliders twelve columns'),
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
        ], className = 'sliders twelve columns') 

    )

if __name__ == '__main__':
    app.run_server(debug=True)