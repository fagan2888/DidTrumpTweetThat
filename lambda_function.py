"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

# --------------- Helpers that build all of the responses ----------------------

import boto3
import json
from boto3.dynamodb.conditions import Key, Attr
import random
import os


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for playing Did Trump Tweet That" \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_answer_response(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "correctAnswer" in session.get('attributes', {}):
        correct_answer = session['attributes']['correctAnswer']
        if correct_answer == "Donald J. Trump":
            speech_output = "Donald Trump did tweet that."
        else:
            speech_output = "No, " + correct_answer + " tweeted that."
        
        should_end_session = True
    else:
        speech_output = "I don't know what the answer is."
        should_end_session = True
        
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

def get_tweet_from_dynamo(handle):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=os.environ.get("ACCESS_KEY"), aws_secret_access_key=os.environ.get("SECRET_KEY"))
    table = dynamodb.Table('TrumpTweet')
    
    max_num = max(table.item_count, 20)
    rand_row = random.randint(0, max_num - 1)
    
    response = table.query(
    KeyConditionExpression=Key("handle").eq(handle)
    & Key('uid').eq(rand_row)
)
    if len(response["Items"]) == 0:
        return None
    return response["Items"][0]

def get_tweet():
    #if np.random.randint(2) == 0:
    #    handle = "realDonaldTrump"
    #else:
    #    handle = 
    
    handle = "realDonaldTrump"
    response = get_tweet_from_dynamo(handle)
    if response == None:
        return ("NA", "NA")
    return (response["name"], response["tweet"])

def get_tweet_response(intent, session):
    tweet = get_tweet()
    session_attributes = {
        "correctAnswer": tweet[0]
    }
    card_title = "Tweet"
    speech_output = '<speak>Did Donald Trump tweet this: <break time="1s"/>' + tweet[1] + '</speak>'
    reprompt_text = '<speak>Did Donald Trump tweet this: <break time="1s"/>' + tweet[1] + '</speak>'
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_tweet_response(None, session)


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetTweetIntent":
        return get_tweet_response(intent, session)
    elif intent_name == "GetAnswerIntent":
        return get_answer_response(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_tweet_response(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
