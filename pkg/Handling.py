from pkg import app
import json
from datetime import datetime
import requests,random,secrets,os,re
from pkg.models import db,User,Doctor,Project,BlogPost,PodcastEpisode,Donation,Volunteer,Partnership,ContactMessage,PersonalDetail,InsuranceInfo,HealthHistory,DoctorInformation,DoctorMedhistory,DoctorLicense
from flask import request,render_template,redirect,flash,session,url_for,jsonify,abort
from markupsafe import escape
from flask_wtf.csrf import CSRFError
# from flask_mail import Message  
# from pkg import mail
# from pkg.extensions import mail, csrf
from itsdangerous import URLSafeTimedSerializer  

from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps








@app.route('/search/', methods=['GET', 'POST'])  
def search():  
    if request.method == 'POST':  
        search_query = request.form['search_query']  
        doctors = Doctor.query.filter(  
            (Doctor.name.like(f'%{search_query}%')) |  
            (Doctor.specialty.like(f'%{search_query}%')) |  
            (Doctor.hospital.like(f'%{search_query}%'))  
        ).all()  
        return render_template('search_results.html', doctors=doctors)  

    return render_template('index.html')