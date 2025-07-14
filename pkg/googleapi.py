# import os
# from flask import Flask, request, redirect, url_for, render_template, session, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'
# app.config['SESSION_COOKIE_NAME'] = 'your_session_cookie_name'

# # Database setup for local calendar events
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'  # Local SQLite database
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# # Define the Event model
# # Define the Attendee model
# class Attendee(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True, nullable=False)

# # Update the Event model to create a relationship with Attendee
# class Event(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False)
#     end_time = db.Column(db.DateTime, nullable=False)
#     attendees = db.relationship('Attendee', secondary='event_attendee', backref='events')

# # Create an association table for many-to-many relationship
# event_attendee = db.Table('event_attendee',
#     db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
#     db.Column('attendee_id', db.Integer, db.ForeignKey('attendee.id'), primary_key=True)
# )

# @app.route('/attendees', methods=['GET'])
# def list_attendees():
#     attendees = Attendee.query.all()
#     return render_template('attendees.html', attendees=attendees)

# @app.route('/add_attendee', methods=['POST'])
# def add_attendee():
#     email = request.form['email']
#     if email:
#         new_attendee = Attendee(email=email)
#         db.session.add(new_attendee)
#         db.session.commit()
#     return redirect(url_for('list_attendees'))

# @app.route('/create_event_page')
# def create_event_page():
#     attendees = Attendee.query.all()  # Fetch all attendees for the event form
#     return render_template('create_event.html', attendees=attendees)
# # Create the database before the first request

# @app.before_first_request
# def create_tables():
#     db.create_all()


# GOOGLE_CREDENTIALS_FILE = 'credentials.json'
# SCOPES = [
#     "https://www.googleapis.com/auth/calendar",
#     "https://www.googleapis.com/auth/calendar.events"
# ]

# @app.route('/doc_api')
# def doc_api():
#     return render_template('doc_api.html')

# # Google Calendar authorization
# @app.route('/authorize')
# def authorize():
#     flow = Flow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES)
#     flow.redirect_uri = url_for('oauth2callback', _external=True)

#     authorization_url, state = flow.authorization_url(access_type='offline')
#     session['state'] = state
#     return redirect(authorization_url)

# @app.route('/oauth2callback')
# def oauth2callback():
#     flow = Flow.from_client_secrets_file(GOOGLE_CREDENTIALS_FILE, SCOPES, state=session['state'])
#     flow.redirect_uri = url_for('oauth2callback', _external=True)

#     authorization_response = request.url
#     flow.fetch_token(authorization_response=authorization_response)

#     credentials = flow.credentials
#     session['credentials'] = credentials_to_dict(credentials)
#     return redirect(url_for('calendar'))  # Redirect to local calendar

# # Local calendar routes
# @app.route('/calendar')
# def calendar():
#     events = Event.query.all()
#     return render_template('Local.html', events=events)

# @app.route('/create_event_page')
# def create_event_page():
#     return render_template('create_event.html')

# @app.route('/create_event', methods=['POST'])
# def create_event():
#     title = request.form['title']
#     start_time = datetime.fromisoformat(request.form['start_time'])
#     end_time = datetime.fromisoformat(request.form['end_time'])

#     new_event = Event(title=title, start_time=start_time, end_time=end_time)
#     db.session.add(new_event)
#     db.session.commit()

#     return redirect(url_for('calendar'))

# @app.route('/create_event_google', methods=['POST'])
# def create_event_google():
#     if 'credentials' not in session:
#         return redirect('authorize')

#     credentials = Credentials(**session['credentials'])

#     # Create a Google Calendar API service
#     try:
#         service = build('calendar', 'v3', credentials=credentials)

#         # Gather event information
#         title = request.form['title']
#         start_time = request.form['start_time']
#         end_time = request.form['end_time']

#         event = {
#             "summary": title,
#             "description": "Appointment via Flask App",
#             "start": {
#                 "dateTime": start_time,
#                 "timeZone": "UTC"
#             },
#             "end": {
#                 "dateTime": end_time,
#                 "timeZone": "UTC"
#             },
#             "conferenceData": {
#                 "createRequest": {
#                     "requestId": "sample123",
#                     "conferenceSolutionKey": {
#                         "type": "MedicalMeet"
#                     }
#                 }
#             },
#             "attendees": [
#                 {"email": "youremail@example.com"},  # Change to actual attendee emails
#             ]
#         }

#         event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
#         meet_link = event.get('hangoutLink')  # The Google Meet link
#         return jsonify({"message": "Event created!", "meet_link": meet_link}), 201

#     except HttpError as error:
#         return jsonify({"error": str(error)}), 400
#     except Exception as e:
#         print("An error occurred!", e)
#         return jsonify({"error": "Failed to create the appointment."}), 400

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('doc_api'))

# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

# if __name__ == '__main__':
#     app.run(debug=True)