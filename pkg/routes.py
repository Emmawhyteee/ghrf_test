from pkg import app
import json
from datetime import datetime
import requests,random,secrets,os
from flask import request,render_template,redirect,flash,session,url_for,jsonify
from markupsafe import escape
from flask_wtf.csrf import CSRFError
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps








# from flask_cors import CORS  # Import CORS
from pkg.models import (db,
                        User,
                        Appointment,
                        Doctor,
                        Project,
                        BlogPost,
                        PodcastEpisode,
                        Donation,
                        Volunteer,
                        Partnership,
                        ContactMessage,
                        PersonalDetail,
                        InsuranceInfo,
                        HealthHistory,
                        DoctorInformation,
                        DoctorMedhistory,
                        DoctorLicense
                        )






# inputting the bot
   
@app.route('/bott/')
def bott():
    return render_template('bot.html')

@app.route('/')
def landing():
    return render_template('index.html', title='Home')

@app.route('/about/')
def about():
    return render_template('about.html',title='About')

@app.route('/projects/')
def project():
    return render_template('projects.html',title='Projects')

@app.route('/emergency/')
def emergency():
    return render_template('emergency.html',title='Emergency')

@app.route('/contact/')
def contact():
    return render_template('contact_us.html',title='Contact')

@app.route('/services/')
def services():
    return render_template('services.html',title='Our Services')

@app.route('/get_involved/')
def get_involved():
    return render_template('get_involved.html',title='Get Involved')

    

@app.route('/podcast/')
def podcast():
    return render_template('podcast.html',title='Podcast')

@app.route('/blog/')
def blog():
    return render_template('blog.html',title='Blog')


# doctor dashboard start....................
@app.route('/doc_dashboard/')
def doc_dashboard():
    id = session.get('user_online')    
    doc=db.session.query(Doctor).filter(Doctor.id==id).first()

     # Retrieve appointments for the doctor
    appointments = Appointment.query.filter(Appointment.doctor_id == id).all()  # Assuming you have a doctor_id in Appointment model


    
    # Get doctor's full name from DoctorInformation
    doctor_info = doc.doctor_information  # This will give you the related DoctorInformation object

    return render_template('doc_dash.html', doc=doc, doctor_info=doctor_info, title='doc|dashboard')

@app.route('/doc_appointment/')
def doc_appointment():
    return render_template('doc_appointment.html', title='doc|dashboard')

@app.route('/doc_message/')
def doc_message():
    return render_template('doc_message.html', title='doc|dashboard')

@app.route('/doc_profile/')
def doc_profile():
    return render_template('doc_profile.html', title='doc|dashboard')

@app.route('/doc_settings/')
def doc_settings():
    return render_template('doc_settings.html', title='doc|dashboard')

# doctor dashboard end............................
