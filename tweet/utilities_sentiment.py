import pandas as pd
import itertools
import snscrape.modules.twitter as sntwitter
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import re
from wordcloud import WordCloud, STOPWORDS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import snscrape.modules.twitter as sntwitter
import nltk
import time
nltk.download('vader_lexicon') #required for Sentiment Analysis

def scrape_tweets(query, num_days, max_tweets):
  #As long as the query is valid (not empty or equal to '#')...
	if query != '':
		if max_tweets != '' :
			if num_days != '':
				#Creating list to append tweet data
				tweets_list = []
				now = dt.date.today()
				now = now.strftime('%Y-%m-%d')
				yesterday = dt.date.today() - dt.timedelta(days = int(num_days))
				yesterday = yesterday.strftime('%Y-%m-%d')
				start = time.time()
				for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query + ' lang:en since:' +  yesterday + ' until:' + now + ' -filter:links -filter:replies').get_items()):
					if i > int(max_tweets):
						break
					tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])
				print(f"Time taken: {time.time() - start}s")
				#Creating a dataframe from the tweets list above 
				df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
				return df


def scrape_tweets_duration(query, start_date, end_date, max_tweets):
 	#As long as the query is valid (not empty or equal to '#')...
	if query != '':
		if max_tweets != '' :
			#Creating list to append tweet data
			tweets_list = []
			start = time.time()
			for i,tweet in enumerate(sntwitter.TwitterSearchScraper(query + ' lang:en since:' +  start_date + ' until:' + end_date + ' -filter:links -filter:replies').get_items()):
				if i > int(max_tweets):
					break
				tweets_list.append([tweet.date, tweet.id, tweet.content, tweet.username])
			print(f"Time taken: {time.time() - start}s")
			#Creating a dataframe from the tweets list above 
			df = pd.DataFrame(tweets_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
			return df


def cleanTxt(text):
	text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
	text = re.sub('#', '', text) # Removing '#' hash tag
	text = re.sub('RT[\s]+', '', text) # Removing RT
	text = re.sub('https?:\/\/\S+', '', text) # Removing hyperlink
	return text


#Sentiment Analysis
def percentage(part,whole):
	return 100 * float(part)/float(whole)

def find_avg_sentiment(df):
	#Assigning Initial Values
	positive = 0
	negative = 0
	neutral = 0
	#Creating empty lists
	tweet_list1 = []
	neutral_list = []
	negative_list = []
	positive_list = []

	#Iterating over the tweets in the dataframe
	for tweet in df['Text']:
		tweet_list1.append(tweet)
		analyzer = SentimentIntensityAnalyzer().polarity_scores(tweet)
		neg = analyzer['neg']
		neu = analyzer['neu']
		pos = analyzer['pos']
		comp = analyzer['compound']

		if neg > pos:
			negative_list.append(tweet) #appending the tweet that satisfies this condition
			negative += 1 #increasing the count by 1
		elif pos > neg:
			positive_list.append(tweet) #appending the tweet that satisfies this condition
			positive += 1 #increasing the count by 1
		elif pos == neg:
			neutral_list.append(tweet) #appending the tweet that satisfies this condition
			neutral += 1 #increasing the count by 1 

	positive = percentage(positive, len(df)) #percentage is the function defined above
	negative = percentage(negative, len(df))
	neutral = percentage(neutral, len(df))
	
	
	#Converting lists to pandas dataframe
	tweet_list1 = pd.DataFrame(tweet_list1)
	neutral_list = pd.DataFrame(neutral_list)
	negative_list = pd.DataFrame(negative_list)
	positive_list = pd.DataFrame(positive_list)
	#using len(length) function for counting
	#print("Since " + noOfDays + " days, there have been", len(tweet_list1) ,  "tweets on " + query, end='\n*')
	#print("Positive Sentiment:", '%.2f' % len(positive_list), end='\n*')
	#print("Neutral Sentiment:", '%.2f' % len(neutral_list), end='\n*')
	#print("Negative Sentiment:", '%.2f' % len(negative_list), end='\n*')
	
	avg_sentiment = len(positive_list)
	avg_sentiment -= len(negative_list)
	avg_sentiment /= len(df)
	return avg_sentiment

def calculate_sentiment(query, num_days, max_tweets):
	df = scrape_tweets(query, num_days, max_tweets)
	return find_avg_sentiment(df)


# This is no longer being used ig
def calculate_delta_sentiment():
	sent50 = calculate_sentiment("Nifty", 50, 10)
	print("sentiment 50d: ", sent50)
	sent30 = calculate_sentiment("Nifty", 30, 10)
	print("sentiment 30d: ", sent30)
	# d = dict();
	# d['sent50d'] = sent50
	# d['sent30d']   = sent30
	# d['mkt_curr_sent'] = ((sent30 - sent50)/2.0)
	d = {
		'sent50d':sent50,
		'sent30d':sent30,           
		'mkt_curr_sent':((sent30 - sent50)/2.0),
	}
	return d

def go_to_parent(path):
	#print("type: ", type(path))
	cnt=0
	for i in path:
		if i=='/':
			index = cnt
		cnt=cnt+1
	path_par = path[0:index]
	return path_par	


# TODO: update this function to check whether today's sentiment update has already been performed or not
# TODO: change sent_arr50 from list of floats to list of dicts('date', 'sentiment')
# If not, then run this function
# If yes, then don't run this function

# Run this function daily
def update_daily_sentiment():
	import os
	path = os.path.abspath(os.curdir)
	path = go_to_parent(path)
	path = go_to_parent(path)
	print("path: ", path) #/Users/avirajbevli/Desktop/Alpha_TermProject/backend/tweet
	path += '/Data_reqd/results/sent_arr50.npy'
	with open(path, 'rb') as f:
	    sent_arr50 = np.load(f)
	print("shape: ", sent_arr50.shape)
	
	sent_arr50 = sent_arr50.tolist() # Needed because for some reason I am not able to modify a numpy array

	print("sent_arr50: ", sent_arr50) #confirmation that sent_arr50 is loading corrrectly
	todays_sentiment = calculate_sentiment("Nifty", 1, 10) # TODO: change to something like 1000000 instead of 10
	print("todays_sentiment: ", todays_sentiment)

	for i in range(49):
		sent_arr50[i] = sent_arr50[i+1]
	sent_arr50[49] = todays_sentiment
	# update sent_arr50 in the stored numpy file(sent_arr50.npy)
	with open(path, 'wb') as f:
		np.save(f, sent_arr50)
	print("sent_arr50: ", sent_arr50) #confirmation that sent_arr50 is loading corrrectly
