#!/usr/bin/env python
#  -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

This sample script leverages the Flask web service micro-framework
(see http://flask.pocoo.org/).  By default the web server will be reachable at
port 5000 you can change this default if desired (see `app.run(...)`).

"""


from dotenv import load_dotenv

__author__ = "Gerardo Chaves"
__author_email__ = "gchaves@cisco.com"
__copyright__ = "Copyright (c) 2016-2021 Cisco and/or its affiliates."
__license__ = "Cisco"

from requests_oauthlib import OAuth2Session
import os
import time
import json
import sys
import datetime as DT

from webexteamssdk import WebexTeamsAPI, ApiError

# load all environment variables
load_dotenv()


AUTHORIZATION_BASE_URL = 'https://api.ciscospark.com/v1/authorize'
TOKEN_URL = 'https://api.ciscospark.com/v1/access_token'
SCOPE = ['spark:all','spark-compliance:events_read', 'spark-compliance:messages_read','spark-compliance:messages_write']
TARGET_MSG_AGE = os.getenv('TARGET_MSG_AGE')
CHECK_EVENTS_FROM_AGE = os.getenv('CHECK_EVENTS_FROM_AGE')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# Initialize the environment

#api = WebexTeamsAPI(access_token=TEST_TEAMS_ACCESS_TOKEN)
api = None


if os.path.exists('tokens.json'):
    with open('tokens.json') as f:
        tokens = json.load(f)
else:
    tokens = None

if tokens == None or time.time()>(tokens['expires_at']+(tokens['refresh_token_expires_in']-tokens['expires_in'])):
    # We could not read the token from file or it is so old that even the refresh token is invalid, so we have to
    # trigger a full oAuth flow with user intervention
    print("Access token not found or expired beyond refresh. Please re-authenticate compliance officer")
    exit()
else:
    # We read a token from file that is at least younger than the expiration of the refresh token, so let's
    # check and see if it is still current or needs refreshing without user intervention
    print("Existing token on file, checking if expired....")
    access_token_expires_at = tokens['expires_at']
    if time.time() > access_token_expires_at:
        print("expired!")
        refresh_token = tokens['refresh_token']
        # make the calls to get new token
        extra = {
            'client_id': os.getenv('CLIENT_ID'),
            'client_secret': os.getenv('CLIENT_SECRET'),
            'refresh_token': refresh_token,
        }
        auth_code = OAuth2Session(os.getenv('CLIENT_ID'), token=tokens)
        new_teams_token = auth_code.refresh_token(TOKEN_URL, **extra)
        print("Obtained new_teams_token: ", new_teams_token)
        # assign new token
        tokens = new_teams_token
        # store away the new token
        with open('tokens.json', 'w') as json_file:
            json.dump(tokens, json_file)
    print("Using stored or refreshed token....")
#Here we should be ready to go with a valid compliance officer token in the tokens variable

# initialize Webex Teams SDK
api = WebexTeamsAPI(access_token=tokens['access_token'])

# setup the time constraint variables to specify for events.list
fromTime=DT.datetime.utcfromtimestamp(time.time()-int(CHECK_EVENTS_FROM_AGE)).isoformat()+'Z'
toTime=DT.datetime.utcfromtimestamp(time.time()-int(TARGET_MSG_AGE)).isoformat()+'Z'

# call events.list to retrieve all created messages events in the timeframe specified
events=api.events.list(resource='messages',type='created',_from=fromTime, to=toTime)

# store all messages in direct spaces in the time frame specified in the toDeleteList list
toDeleteList=[]
for theEvent in events:
    #print(theEvent)
    if theEvent.data.roomType=='direct':
        toDeleteList.append(theEvent.data)

# iterate through the list of messages to delete to show on console before deleting
listLength=len(toDeleteList)
print(f'Ready to delete {listLength} messages:')
for theMessage in toDeleteList:
    print(f'at {theMessage.created} from {theMessage.personEmail} with ID {theMessage.id}')
# confirm deletion of messages NOTE: remove the line below if you want to skip confirmation
if not input("Procced? (y/n): ").lower().strip()[:1] == "y": sys.exit(1)

# iterate through toDeleteList to delete all messages there
for theMessage in toDeleteList:
    print(f'Deleting message at {theMessage.created} from {theMessage.personEmail} with ID {theMessage.id}')
    try:
        api.messages.delete(theMessage.id)
    except ApiError as e:
        if e.status_code==404:
            print('Message already deleted....')
        else:
            print(e)