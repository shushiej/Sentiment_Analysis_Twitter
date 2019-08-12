## Twitter Sentiment Analysis

This repository is a playground to apply NLP techniques on twitter threads.
Currently there exists a class that gets the last 200 tweets from any twitter handle and writes it to a database. This is then picked up by a python file which plots the twitter metrics to a frontend server using Dash and Plotly. 

### Things to do before using project

* Rename the `cred_sample.py` to `creds.py` and fill out the neccessary information.
    * You can set up the keys and tokens from: [Twitter Apps](http://apps.twitter.com) (assuming you have a twitter account)
* start a `pipenv` environment this is especially useful for the Dash and Plotly server. You can install and use it from [here](https://docs.pipenv.org/en/latest/install/)
* One of the methods uses the ldamalletmodel which needs to be downloaded to a directory of your choice. This can be downloaded from [here](http://mallet.cs.umass.edu/download.php). 
* Make sure you have sqlite3 installed on your computer. 

### TO DO
* Apply NLP techniques using Spacy, Gensim and scikit learn about topic modelling [X]
* Generate user word clouds [X]
* Write twiiter data into a SQLite Database [X]
* Generate Dash frontend to display twitter metrics [X]
* Write a scheduler that inserts new twitter data into DB.
* Create new model to analyse twitter sentiments, instead of using TextBlob.
* Get Like Factor for user. 
    - Get collection of twitter replies and create a senitment polarity ratio (postive : negative replies) for the users tweets
* Get tweets by sentiment
* Av Time for Tweet response by followers
* Design most liked/ most retweeted and least liked tweet similar to twitter design.
* Twitter Len vs Twitter Engagement Analysis
* Deploy to Github Pages.
* Develop a Stock price for each user based on the like factor. 