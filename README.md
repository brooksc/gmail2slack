# gmail2slack


This program will monitor your gmail inbox and when you receive a new email, it will send you a notification on slack.

This is useful if you spend your day in slack talking with your team and at times forget that the rest of the world still uses email.

Installation

1. Download this script
2. run `pip install -r requirements.txt` to install the various libraries required

## Configuration


gmail2slack config files by default are stored in the directory ~/.config/gmail2slack.  Create this directory.

### Get a Gmail API Key
Next you'll need a Gmail API Key

1. Obtain a google API key by visiting https://console.developers.google.com/project, create a project
2. Once created, select the project and enable the Gmail API
3. Under Oauth Select Create New Client ID
4. Select Installed Application and click Configure
5. Select your email address, enter a product name like gmail2slack.  Click Save
6. Click Installed Application again and Other
7. You should now have a Client ID for Native Application.  You'll need the Client ID and Client Secret later...

### Create default_cs.json config

Next you'll want to create a file with a name of ~/.config/gmail2slack/default_cs.json

Add this file:
```
{
  "installed": {
    "client_id": "foo",
    "client_secret":"foo",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token"
  }
}
```

But replace the foo value in client_id and client_secret with what you generated from the gmail APi

### Get a Slack API Key

Next, get a Slack API key.

1. Visit https://api.slack.com/
2. Sign in if you need to
3. Click Get Token

### Create default.yaml

Last step - add the following to ~/.config/gmail2slack/default.yaml
```
slack_apikey: foo
slack_user: yourname
slack_from: gmail2slack
client_secret: default_cs.json
gmail2slack_pickle: default.pickle
gmail2slack_oauth: default.oauth
gmail_storage: default.gmail
```

Change foo to the slack API key
Change yourname to your alias in slack

The rest you can leave as is.

## Let's run this thing!

### Run Once

If you are using the default_cs.json and default.yaml in ~/.config/gmail2slack as described above, then just run

`gmail2slack`

It will check your inbox, send any slack notifications and exit.  This should be good for running fron cron, etc.

When you run the script the first time, it will open a local browser (if possible) and ask you to sign in to gmail and give the script access to your gmail account.

### Run Forever

If you want to have it loop forever and sleep in between checks, run it with the -l command with an argument of the number of seconds to sleep.  For example

`gmail2slack -l 60`

## Use a different config file

You can use the -c option to specify another directory for the config files, like

`gmail2slack -c ~/.gmail2slack.cfg`

For the following keys:

```
client_secret: default_cs.json
gmail2slack_pickle: default.pickle
gmail2slack_oauth: default.oauth
gmail_storage: default.gmail
```

The filenames (e.g. default_cs.json) can be a relative path or fully qualified path (e..g /home/user/default_cs.json).  If it's a relative path, then it will look for the file in the same directory as the config file.

If you have a case where you want to run this script with multiple gmail accounts, you could create a set of files for each account.

## Run from crontab

The easiest way to run this script is from crontab, have it once a minute (or whatever frequency) check for emails.  

since there a number of python dependencies, I use virtualenv to contain them in a directory like ~/.virtualenv/default.  I then created a script like the one below:

```
#!/bin/sh
source ~/.virtualenv/default/bin/activate
~/github/gmail2slack/gmail2slack.py
```

which I saved to gmail2slack.sh and then run `crontab -e` and add a line like:

```
* * * * * ~/brooksc/github/gmail2slack.sh
```

Of course change the paths to match your environment


## Known Issues

None -- I can 
