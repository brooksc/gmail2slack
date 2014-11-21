#!/usr/bin/env python

import pickle
import time
import traceback

import httplib2
import arrow
from oauth2client import tools
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

# from pprint import pprint

from apiclient.discovery import build
from slacker import Slacker
import os
import sys
import argparse
from oauth2client.client import AccessTokenRefreshError


from yaml import load

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Gmail2Slack():
    def __init__(self, config, slack):
        self.slack = slack
        self.config = config

        # Check https://developers.google.com/admin-sdk/directory/v1/guides/authorizing for all available scopes
        OAUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

        # Location of the credentials storage file
        STORAGE = Storage(self.config['gmail_storage'])

        # Start the OAuth flow to retrieve credentials
        flow = flow_from_clientsecrets(config['client_secret'], scope=OAUTH_SCOPE)
        http = httplib2.Http()

        # Try to retrieve credentials from storage or run the flow to generate them
        parser = argparse.ArgumentParser(parents=[tools.argparser])
        flags = parser.parse_args([])

        credentials = None

        storage = Storage(self.config['gmail2slack_oauth'])
        try:
            credentials = storage.get()
        except:
            sys.exit("Unable to retrieve credentials")

        if not credentials:
            credentials = tools.run_flow(flow, STORAGE, flags)

        storage.put(credentials)
        # Authorize the httplib2.Http object with our credentials
        http = credentials.authorize(http)

        # Build the Gmail service from discovery
        self.gmail_service = build('gmail', 'v1', http=http)
        self.user_id = 'me'

        try:
            self.state = pickle.load(open(self.config['gmail2slack_pickle'], "rb"))
        except IOError:
            self.state = dict()
            self.state['timestamp'] = arrow.utcnow().timestamp

            # self.new_timestamp = arrow.utcnow().timestamp # BUG?  Move to gmail2slack?

    def save_state(self):
        # Save timestamp so we don't process the same files again
        # self.state['timestamp'] = self.new_timestamp
        self.state['timestamp'] = arrow.utcnow().timestamp
        pickle.dump(self.state, open(self.config['gmail2slack_pickle'], "wb"))

    def gmail2slack(self):
        try:
            response = self.gmail_service.users().messages().list(userId=self.user_id, labelIds="INBOX").execute()
        except AccessTokenRefreshError:
            return

        message_ids = []
        if 'messages' in response:
            message_ids.extend(response['messages'])
        for msg_id in message_ids:
            message = self.gmail_service.users().messages().get(userId=self.user_id, id=msg_id['id']).execute()
            headers = dict()
            for header in message['payload']['headers']:
                headers[header['name']] = header['value']

            try:  # due to issue @ https://github.com/crsmithdev/arrow/issues/176
                from_ts = arrow.get(headers['Date'], 'ddd, D MMM YYYY HH:mm:ss ZZ').timestamp
            except:
                continue

            if from_ts < self.state['timestamp']:
                break
            from_date = arrow.get(from_ts).to('US/Eastern').format('YYYY-MM-DD HH:mm:ss ZZ')
            say = "New Email\n>From: %s\n>Date: %s\n>Subject: %s\n>\n>%s" % \
                  (headers['From'], from_date, headers['Subject'], message['snippet'])
            self.slack.direct_message(say, self.config['slack_user_id'], self.config['slack_from'])
        self.save_state()


class Slack():
    def __init__(self, apikey):
        self.slack = Slacker(apikey)

    def get_name_id(self, name):
        users = self.slack.users.list()
        user_id = None
        for member in users.body['members']:
            if member['name'] == name:
                user_id = member['id']
                break
        return user_id

    def direct_message(self, message, user_id, slack_from):
        self.slack.chat.post_message(user_id, message, username=slack_from)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="verbosity", action="store_true")
    parser.add_argument("-c", "--config", help="path to gmail2slack.yaml", action="store",
                        default=os.getenv("HOME") + "/.config/gmail2slack/default.yaml")
    parser.add_argument("-l", "--loop", help="loop every x seconds", action="store", default=0)
    args = parser.parse_args()

    try:
        config = load(open(args.config, "r"), Loader=Loader)
    except IOError:
        sys.exit("Unable to open config file %s" % args.config)

    slack = Slack(config['slack_apikey'])
    # validate config
    if not 'slack_user_id' in config:
        config['slack_user_id'] = slack.get_name_id(config['slack_user'])
    if not config['slack_user_id']:
        sys.exit("Could not find slack id for user %s" % config['slack_user'])
    # Make sure all paths are absolute
    if 'dir' not in config or not os.path.isdir(config['dir']):
        config['dir'] = os.path.basename(args.config)
    for key in ['client_secret', 'gmail2slack_pickle', 'gmail2slack_oauth', 'gmail_storage']:
        if not os.path.isabs(config[key]):
            config[key] = "%s/%s" % (os.path.dirname(args.config), config[key])
    if not os.path.isfile(config['client_secret']):
        sys.exit("Unable to open client_secret file %s" % config['client_secret'])

    g2s = Gmail2Slack(config, slack)
    if int(args.loop) > 0:
        delay = int(args.loop)
    else:
        delay = 0
    while True:
        try:
            g2s.gmail2slack()
        except:
            traceback.print_exc()
        if delay:
            time.sleep(delay)
        else:
            break


if __name__ == "__main__":
    main()