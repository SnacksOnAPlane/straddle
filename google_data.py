import gdata.spreadsheets.client
import gdata.spreadsheets.data
import gdata.gauth
import json
import os
from oauth2client.file import Storage

secret_data = json.loads(open('client_secret.json').read())
CLIENTID = secret_data['installed']['client_id']
CLIENTSECRET = secret_data['installed']['client_secret']
home_dir = os.path.expanduser('~')
credential_dir = os.path.join(home_dir, '.credentials')
if not os.path.exists(credential_dir):
  os.makedirs(credential_dir)
credential_path = os.path.join(credential_dir,
                 'sheets.googleapis.com-python-quickstart.json')

store = Storage(credential_path)
pdb.set_trace()
# create the OAuth2 token
token = gdata.gauth.OAuth2Token(client_id=CLIENTID,
                                client_secret=CLIENTSECRET,
                                scope='https://spreadsheets.google.com/feeds/',
                                user_agent='blah.blah',
                                access_token='ACCESSTOKEN',
                                refresh_token='REFRESHTOKEN')

# create the spreadsheet client and authenticate
spr_client = gdata.spreadsheets.client.SpreadsheetsClient()
token.authorize(spr_client)

#create a ListEntry. the first item of the list corresponds to the first 'header' row
entry = gdata.spreadsheets.data.ListEntry()
entry.set_value('ham', 'gary')
entry.set_value('crab', 'sack')

# add the ListEntry you just made
spr_client.add_list_entry(entry, 'SPREADSHEETID', 'od6')
