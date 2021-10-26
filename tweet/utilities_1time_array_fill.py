# This python script will only be run once
# It will populate sent_arr[50]
import numpy as np
import sys
import os
import django

import pandas as pd
import itertools
import snscrape.modules.twitter as sntwitter
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import datetime as dt
import re
from wordcloud import WordCloud, STOPWORDS
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import snscrape.modules.twitter as sntwitter
import nltk
import time
nltk.download('vader_lexicon') #required for Sentiment Analysis


sys.path.append('/Users/avirajbevli/Desktop/Alpha_TermProject/backend')
os.environ['DJANGO_SETTINGS_MODULE'] = 'backend.settings'
django.setup()



def find_prev_50_sents():
	#return np.full(50, 0)
	from utilities_sentiment import scrape_tweets_duration
	from utilities_sentiment import find_avg_sentiment
	max_tweets = 10 # TODO: change to a realistic value
	
	end_date = dt.date.today()
	end_date = end_date.strftime('%Y-%m-%d')
	start_date = dt.date.today() - dt.timedelta(days = 1)
	start_date = start_date.strftime('%Y-%m-%d')

	sent_arr50 = []

	for i in range(50):
		df = scrape_tweets_duration("Nifty", start_date, end_date, max_tweets)
		todays_sentiment = find_avg_sentiment(df)
		print(i,": ", todays_sentiment)
		sent_arr50.append(todays_sentiment)

		end_date = dt.date.today() - dt.timedelta(days = i+1)
		end_date = end_date.strftime('%Y-%m-%d')
		start_date = dt.date.today() - dt.timedelta(days = (i+2))
		start_date = start_date.strftime('%Y-%m-%d')

	return sent_arr50


# print("Arr: ", sent_arr)
# print("type: ", type(sent_arr)) #type:  <class 'numpy.ndarray'>
# print("shape: ", sent_arr.shape) #(50,1)

os.chdir("..") #cd changed from asset to backend
os.chdir("..") #cd changed from backend to Alpha_TermProject
path = os.path.abspath(os.curdir)
path+="/Data_reqd/results/sent_arr50.npy"
print("path: ", path)
sent_arr50 = find_prev_50_sents()
with open(path, 'wb') as f:
    np.save(f, sent_arr50)
