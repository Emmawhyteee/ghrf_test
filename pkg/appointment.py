

from flask import Flask, render_template, request, redirect, url_for  
import datetime  
import os  
import pickle  
from google.auth.transport.requests import Request  
from google.oauth2.credentials import Credentials  
from google_auth_oauthlib.flow import InstalledAppFlow  
from googleapiclient.discovery import build  

SCOPES = ['https://www.googleapis.com/auth/calendar']  
app = Flask(__name__)  

def authenticate_gcal():  
    creds = None  
    if os.path.exists('token.pickle'):  
        with open('token.pickle', 'rb') as token:  
            creds = pickle.load(token)  
    if not creds or not creds.valid:  
        if creds and creds.expired and creds.refresh_token:  
            creds.refresh(Request())  
        else:  
            flow = InstalledAppFlow.from_client_secrets_file('pkg/client_secret_654546899957-pa5klgdd184l2c8u25juukgco9l858eb.apps.googleusercontent.com.json', SCOPES)  
            creds = flow.run_local_server(port=0)  
        with open('token.pickle', 'wb') as token:  
            pickle.dump(creds, token)  
    return creds  

def create_google_meet_event(creds, summary, start, end):  
    service = build('calendar', 'v3', credentials=creds)  

    event = {  
        'summary': summary,  
        'start': {  
            'dateTime': start,  
            'timeZone': 'America/Los_Angeles',  
        },  
        'end': {  
            'dateTime': end,  
            'timeZone': 'America/Los_Angeles',  
        },  
        'conferenceData': {  
            'createRequest': {  
                'requestId': 'some-random-string',  
                'conferenceSolutionKey': {  
                    'type': 'hangoutsMeet',  
                },  
            }  
        },  
        'reminders': {  
            'useDefault': False,  
            'overrides': [  
                {'method': 'email', 'minutes': 24 * 60},  
                {'method': 'popup', 'minutes': 10},  
            ],  
        },  
    }  

    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()  
    return event  

@app.route('/')  
def Local():  
    return render_template('Local.html', events='')  

@app.route('/create_event', methods=['POST'])  
def create_event():  
    summary = request.form['summary']  
    start = request.form['start']   
    end = request.form['end']        
    
    creds = authenticate_gcal()  
    try:  
        event = create_google_meet_event(creds, summary, start, end)  
        return redirect(url_for('Local'))  
    except Exception as e:  
        return f"An error occurred: {e}"  

if __name__ == '__main__':  
    app.run(debug=True)