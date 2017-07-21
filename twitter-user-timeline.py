#!/usr/bin/python

#-----------------------------------------------------------------------
# twitter-user-timeline
#  - displays a user's current timeline.
#-----------------------------------------------------------------------

from twitter import *
import boto3
import json
#-----------------------------------------------------------------------
# load our API credentials
#-----------------------------------------------------------------------
config = {}
execfile("config.py", config)

ddb = boto3.resource('dynamodb')
table = ddb.Table('TrumpTweet')

#-----------------------------------------------------------------------
# create twitter API object
#-----------------------------------------------------------------------
twitter = Twitter(
		auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

#-----------------------------------------------------------------------
# this is the user we're going to query.
#-----------------------------------------------------------------------
user = "realDonaldTrump"

#-----------------------------------------------------------------------
# query the user timeline.
# twitter API docs:
# https://dev.twitter.com/rest/reference/get/statuses/user_timeline
#-----------------------------------------------------------------------
results = twitter.statuses.user_timeline(screen_name = user, count = 200)

#-----------------------------------------------------------------------
# loop through each status item, and print its content.
#-----------------------------------------------------------------------

for ind,status in enumerate(results):
	item = {
            'handle':status['user']['screen_name'],
            'uid':ind,
            'name':status['user']['name'],
            'tweet':status['text']
        }
	table.put_item(Item=item)

# print "%s %s" % (status["id"], status["text"].encode("ascii", "ignore"))







