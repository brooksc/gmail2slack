gmail2slack
===========

This program will monitor your gmail inbox and when you receive a new email, it will send you a notification on slack.

This is useful if you spend your day in slack talking with your team and at times forget that the rest of the world still uses email.

Installation

1. Download this script
2. run `pip -r requirements.txt` to install the various libraries required

Configuration

gmail2slack config files by default are stored in the directory ~/.config/gmail2slack.  Create this directory.

Next you'll need a Gmail API Key

1. Obtain a google API key by visiting https://console.developers.google.com/project, create a project
2. Once created, select the project and enable the Gmail API
3. Under Oauth Select Create New Client ID
4. Select Installed Application and click Configure
5. Select your email address, enter a product name like gmail2slack.  Click Save
6. Click Installed Application again and Other
7. You should now have a Client ID for Native Application.  You'll need the Client ID and Client Secret later...

Next you'll want to create a file with a name of ~/.config/gmail2slack/default_cs.json

Add this file:

{
  "installed": {
    "client_id": "foo",
    "client_secret":"foo",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}

But replace the foo value in client_id and client_secret with what you generated from the gmail APi

Next, get a Slack API key.

1. Visit https://api.slack.com/
2. Sign in if you need to
3. Click Get Token

Last step - add the following to ~/.config/gmail2slack/default.yaml

slack_apikey: foo
slack_user: yourname
slack_from: gmail2slack
client_secret: default_cs.json
gmail2slack_pickle: default.pickle
gmail2slack_oauth: default.oauth
gmail_storage: default.gmail

Change foo to the slack API key
Change yourname to your alias in slack

The rest you can leave as is.









