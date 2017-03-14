from __future__ import print_function
import httplib2
import os
import pdb

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
  import argparse
  flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
  flags = None

class GoogleSheet:
  # If modifying these scopes, delete your previously saved credentials
  # at ~/.credentials/sheets.googleapis.com-python-quickstart.json
  SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
  CLIENT_SECRET_FILE = 'client_secret.json'
  APPLICATION_NAME = 'Google Sheets API Python Quickstart'

  def __init__(self, id, sheet_id):
    self.sheet = self.get_sheet()
    self.id = id
    self.sheet_id = sheet_id

  def get_credentials(self):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
      Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
      os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                     'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
      flow = client.flow_from_clientsecrets(GoogleSheet.CLIENT_SECRET_FILE, GoogleSheet.SCOPES)
      flow.user_agent = GoogleSheet.APPLICATION_NAME
      if flags:
        credentials = tools.run_flow(flow, store, flags)
      else: # Needed only for compatibility with Python 2.6
        credentials = tools.run(flow, store)
      print('Storing credentials to ' + credential_path)
    return credentials

  def get_sheet(self):
    credentials = self.get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
            'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                  discoveryServiceUrl=discoveryUrl)
    return service.spreadsheets()

  def update(self, data):
    value = lambda x: { "userEnteredValue": {"stringValue": str(x)} }
    rows = [{"values": [value(cell) for cell in row]} for row in data]
    body = {
      "requests": [
        {
          "appendCells": {
            "sheetId": self.sheet_id,
            "rows": rows,
            "fields": "*",
          }
        }
      ],
    }
    self.sheet.batchUpdate(spreadsheetId=self.id, body=body).execute()


if __name__ == '__main__':
  sheet = GoogleSheet()
  sheet.update([['blah','price'], ['foo','thing']])

