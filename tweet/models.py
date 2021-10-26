from django.db import models

from .models import *
import itertools
from datetime import datetime  # to convert python's dateTime to unix time

import pandas as pd
import snscrape.modules.twitter as sntwitter
from django.db import models
from django.utils import timezone





#####################################################################################################
#####################################  We are not using models as of now ############################
#####################################################################################################





# # Create your models here.
def calculate_sentiment(content):
    return 0.5

class TwitterUser(models.Model):
	twitter_id = models.CharField(max_length=100, unique=True) 
	#last_tweet_date_time = models.DateTimeField(default=timezone.now)  
	# Each time we look for new tweets from this ID, only look from a time beyong this time
	def __str__(self):
		return self.twitter_id
	class Meta:
		verbose_name = "Twitter User",
		verbose_name_plural = 'Twitter Users'


class Tweet(models.Model):
	#tweeter_id = models.ForeignKey(TwitterUser, on_delete=models.CASCADE, null=False)  # Every tweet must have an assosiated ID
	tweeter_id = models.CharField(max_length=100, unique=True)
	url = models.CharField(max_length=100, null=True)
	tweet_id = models.CharField(max_length=100, null=True)
	content = models.CharField(max_length=5000, unique=False)
	time = models.DateTimeField(default=timezone.now)
	sentiment_score = models.FloatField() # sentiment_score lies in [-1,1]
	def __str__(self):
		return self.content
	class Meta:
		verbose_name = "Tweet",
		verbose_name_plural = 'Tweets'	

	@classmethod
	def get_twitter(cls, query, num):
		import snscrape.modules.twitter as sntwitter
		print("fetching data of " + query + ", no of tweets = " + str(num))
		df = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(query).get_items(), num))
		return df

	# When called, this function updates the whole table by fetching new tweets
	@classmethod
	def update_me(cls):
		import pandas as pd
		print("#################### updating tweets #####################")
		num = 3
		# since_date = "2021-05-07" #yyyy-mm-dd, not being used
		twitter_user_list = TwitterUser.objects.all()
		df = pd.DataFrame()
		for twtr_user in twitter_user_list:
			print('Twitter id: ', twtr_user.twitter_id)
			last_date_time_tweet = twtr_user.last_tweet_date_time
			last_timestamp = datetime.timestamp(last_date_time_tweet)
			print('Last tweet time: ', last_timestamp)
			x_str = str(last_timestamp)
			x = x_str.split(".")
			since_time = x[0]  # we want only the before . part of the time stamp in our query
			# query = "from:"+twitter_user.user_twitter_id+" since:"+since_date
			query = "from:" + twtr_user.twitter_id + " since_time:" + since_time
			df_temp = cls.get_twitter(query, num)
			df = df.append(df_temp)
		
		cols_to_take_list = ['content']
		print('HI')
		for index, row in df.iterrows():
			print("ROW: ", row)
			if Tweet.objects.filter(tweet_id=row['id']).exists():
				print("this tweet already exists.")
				continue
			with open('log.csv', "w+") as file:
				for item in row:
					file.write(str(item))
					file.write(',')
				file.write('\n')

			# print("type: ", type(row['id']))
			# print("type: ", type(row['user']))
			# print("just above")
			# id_temp = row['user']['username']
			# print("type: ", type(id_temp))
			# # id_temp = int(id_temp)
			# # print("type: ", type(id_temp))
			# twtr_user = TwitterUser.objects.get(twitter_id=id_temp)
			# print("just below")
			# twtr_user.last_tweet_date_time = datetime.now()  # Update the most recent tweet time of the user to "now" in the database
			# print("HI")
			# twtr_user.save() #update the last tweet time of this twitter user
			# print("SAved")

			twt = Tweet(
				tweeter_id=row['user']['username'],
				url=row['url'],
				tweet_id=row['id'],
				content=row['content'],
				time=row['date'],
				sentiment_score=calculate_sentiment(row['content']),
			)
			# Save tweet in database
			twt.save()
			print("saved tweet")
		print("Successfully updated tweets in database")