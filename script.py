from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime

def timestamp():
    date = datetime.datetime.now()
    if date.minute < 10:
        minuten = '0' + str(date.minute)
    else:
        minuten = date.minute
    if date.hour < 10:
        uren = '0' +str(date.uren)
    else:
        uren = date.hour
    time = str(uren) + ':' + str(minuten)
    isoDate = str(date.day) + '/' + str(date.month) + '/' + str(date.year)

    response = {
        'time' : time,
        'date' : isoDate
    }
    
    return response

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


SAMPLE_SPREADSHEET_ID = '1pVRPdzwC1xMCwZP5aeuxXtsE2Y3SPiVBFwPeY00snug'
SAMPLE_RANGE_NAME = 'A2:D1000'

#connect
creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()

#alle temperaturen in sheet
def matrix():
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('tijd, temperatuur, vochtigheid, datum:')
        for row in values:
            print('%s, %s, %s, %s' % (row[0], row[1], row[2], row[3]))

#alle data in returns
def allData():
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    return result.get('values', [])

#laatst toegevoegde temperatuur set --> discord
def lastData():
    values = allData()
    value = values[len(values) - 1]
    print(value)

class Sample():
    def __init__(self, temp, vocht):
        self.temperatuur = temp
        self.vochtigheid = vocht
    
    def create(self):
        values = allData()
        LAST_INDEX = len(values) + 2
        NEW_RANGE = 'A{}:D{}'.format(str(LAST_INDEX), str(LAST_INDEX))
        metadata = timestamp()
        values = [
            [
                metadata['time'], self.temperatuur, self.vochtigheid, metadata['date']
            ]
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=SAMPLE_SPREADSHEET_ID, range=NEW_RANGE,
            valueInputOption='USER_ENTERED', body=body).execute()
        print('{0} cells updated.'.format(result.get('updatedCells')))
    
    def controle(self):
        if not self.temperatuur:
            self.temperatuur = 'unknown'
            return False
        elif not self.vochtigheid:
            self.vochtigheid = 'unknown'
            return False
        else:
            return True


newsample = Sample(25, '15%')
sampleTest = newsample.controle()
if sampleTest is not True:
    print("False sample")
else:
    newsample.create()

matrix()
lastData()