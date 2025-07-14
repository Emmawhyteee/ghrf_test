from flask import Flask, request, jsonify, render_template, redirect, url_for, session  
from flask_mysqldb import MySQL  
from flask_cors import CORS  
from google_auth_oauthlib.flow import Flow  
from googleapiclient.discovery import build  
import os  

app = Flask(__name__)  
app.secret_key = 'emmawhyte12345'  
CORS(app)  

# Google Calendar API config  
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Enable insecure transport (for local testing purposes)  

# Your MySQL config  
app.config['MYSQL_HOST'] = 'mysql+mysqlconnector://root@127.0.0.1/ghrf'  
app.config['MYSQL_USER'] = 'your_user'  
app.config['MYSQL_PASSWORD'] = 'your_password'  
app.config['MYSQL_DB'] = 'appointment_system'  

mysql = MySQL(app)  

# Constants for Google Calendar API  
CLIENT_SECRETS_FILE = "client_secret_654546899957-as82fkd76kil1vb71tka4enqmbfrtplq.apps.googleusercontent.com"  #credential json was here
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]  

# OAuth 2.0 Flow  
@app.route('/login')  
def login():  
    flow = Flow.from_client_secrets_file(  
        CLIENT_SECRETS_FILE,  
        scopes=SCOPES,  
        redirect_uri=url_for('callback', _external=True)  
    )  
    authorization_url, state = flow.authorization_url(access_type='offline')  
    session['state'] = state  
    return redirect(authorization_url)  

@app.route('/callback')  
def callback():  
    flow = Flow.from_client_secrets_file(  
        CLIENT_SECRETS_FILE,  
        scopes=SCOPES,  
        state=session['state'],  
        redirect_uri=url_for('callback', _external=True)  
    )  
    flow.fetch_token(authorization_response=request.url)  
    credentials = flow.credentials  
    session['credentials'] = credentials_to_dict(credentials)  
    return redirect(url_for('index'))  

@app.route('/')  
def index():  
    return render_template('index.html')  

@app.route('/appointments', methods=['POST'])  
def book_appointment():  
    data = request.json  
    patient_id = data['patient_id']  
    doctor_id = data['doctor_id']  
    appointment_date = data['appointment_date']  
    
    # Store the appointment in MySQL  
    cur = mysql.connection.cursor()  
    cur.execute("INSERT INTO appointments(patient_id, doctor_id, appointment_date) VALUES (%s, %s, %s)",   
                (patient_id, doctor_id, appointment_date))  
    mysql.connection.commit()  
    cur.close()  

    # Add appointment to Google Calendar  
    if 'credentials' in session:  
        service = build('calendar', 'v3', credentials=session['credentials'])  
        event = {  
            'summary': f'Appointment with Patient {patient_id}',  
            'start': {  
                'dateTime': appointment_date,  
                'timeZone': 'America/Los_Angeles',  # Change to your time zone  
            },  
            'end': {  
                'dateTime': appointment_date,  # Adjust for appointment duration  
                'timeZone': 'America/Los_Angeles',  
            },  
        }  
        service.events().insert(calendarId='primary', body=event).execute()  
    
    return jsonify({'message': 'Appointment booked successfully and added to Google Calendar'})  

def credentials_to_dict(credentials):  
    return {  
        'token': credentials.token,  
        'refresh_token': credentials.refresh_token,  
        'token_uri': credentials.token_uri,  
        'client_id': credentials.client_id,  
        'client_secret': credentials.client_secret,  
        'scopes': credentials.scopes  
    }  

if __name__ == "__main__":  
    app.run(debug=True)
