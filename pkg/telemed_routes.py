from pkg import app
import json
from datetime import datetime
import requests,random,secrets,os,re
from pkg.models import db,Appointment,User,Doctor,Project,BlogPost,PodcastEpisode,Donation,Volunteer,Partnership,ContactMessage,PersonalDetail,InsuranceInfo,HealthHistory,DoctorInformation,DoctorMedhistory,DoctorLicense
from flask import request,render_template,redirect,flash,session,url_for,jsonify,abort
from markupsafe import escape
from flask_wtf.csrf import CSRFError
from pkg import csrf
from itsdangerous import URLSafeTimedSerializer  
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from flask import Flask
from flask_jwt_extended import create_access_token,decode_token,jwt_required,get_jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
import jwt
from dotenv import load_dotenv

load_dotenv()

def login_required(f):
    @wraps(f)
    def check_login(*args,**kwargs):
        if session.get('user_online') != None:
            return f(*args,**kwargs)
        else:
            flash('You must be logged in to access this page', category='error')
            return redirect('/vcsignin/')
    return check_login

# def api_login_required(f):
#     def decorator(f):    
#         @wraps(f)
#         def check_login(*args,**kwargs):
#             auth_header = request.headers.get('Authorization')
#             if not auth_header:
#                 return jsonify({"message": "Missing Authorization Header"}),401
#             try:
#                 payload = decode_token(auth_header)
#                 user_id = payload['sub']
#                 user_role = payload['role'] 

#                 if f and user_role != f:
#                     return jsonify({"message":"Unauthorized access"}), 403
            
                
#         return check_login

#.............................................................................11111111111111111111111

# def api_login_required(expected_role=None):
#     def decorator(f):
#         @wraps(f)
#         def check_login(*args, **kwargs):
#             auth_header = request.headers.get('Authorization')
#             if not auth_header:
#                 return jsonify({"message": "Missing Authorization Header"}), 401
            
#             # Extract the token from the header
#             token = auth_header.split(" ")[1]  # Assuming the format is "Bearer <token>"
#             try:
#                 # Decode the token to get the payload
#                 payload = decode_token(token)
                
#                 # Extract id and role from the payload
#                 user_id = payload['sub']  # 'sub' is the default claim for identity
#                 user_role = payload.get('role')  # Assuming you added 'role' to the token

                
#                 user = db.session.query(User).filter(User.id == user_id).first()
#                 doctor = db.session.query(Doctor).filter(Doctor.id == user_id).first()

#                 #for doctors           
#                 if not doctor:
#                     return jsonify({"message": "User  not found"}), 404
#                 else:
#                     user_role='doctor'
#                     return  jsonify({'id': user_id, 'role': 'doctor'}),200
#                 #for users   
#                 if not user:
#                     return jsonify({"message": "User  not found"}), 404
#                 else:
#                     user_role='patient'
#                     return  jsonify({'id': user_id, 'role': 'patient'}),200
                    

                   


#                 # Validate the role if expected_role is provided
#                 if expected_role and user_role != expected_role:
#                     return jsonify({"message": "Unauthorized access"}), 403

#                 # Optionally, you can validate the user_id against your database
#                 # For example:
#                 # user = db.session.query(User).filter_by(id=user_id).first()
#                 # if not user:
#                 #     return jsonify({"message": "User  not found"}), 404

#             except Exception as e:
#                 return jsonify({"message": "Invalid token", "error": str(e)}), 401
            
#             return f(*args, **kwargs)  # Call the original function with the arguments

#         return check_login
#     return decorator
#.............................................................................222222222222222222
#.............................................................................
def api_login_required(roles_required):
    def decorator(f):
        @wraps(f)
        def check_login(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"message": "Missing Authorization Header"}), 401
            
            # Extract the token from the header
            token = auth_header.split(" ")[1]  # Assuming the format is "Bearer <token>"
            
            # try:
            # Decode the token to get the payload
            print('1')
            payload = jwt.decode(token,os.getenv('JWT_SECRET_KEY') , algorithms=["HS256"] )
            print('2')
            
            # Extract id and role from the payload
            user_id = payload['id']
            user_role = payload['role'] 
            print(user_role)

            # Check if the user is a doctor
            if user_role == 'doctor':
                doctor = db.session.query(Doctor).filter(Doctor.id == user_id).first()
                if not doctor:
                    return jsonify({"message": "Invalid credentials: Doctor not found"}), 401
                return f(*args, **kwargs)  # Proceed to the protected route

            # Check if the user is a patient
            if user_role == 'patient':
                user = db.session.query(User).filter(User.id == user_id).first()
                if not user:
                    return jsonify({"message": "Invalid credentials: User not found"}), 401
                return f(*args, **kwargs)  # Proceed to the protected route

            # If the user's role is not in the required roles
            if user_role not in roles_required:
                return jsonify({"message": "Unauthorized access: Role not permitted"}), 403
                    
            # except Exception as e:
            #     return jsonify({"message": "Invalid token", "error": str(e)}), 401
            
        return check_login
    return decorator

#.............................................................................
def get_user_by_id(id):
    deets = db.session.query(User).get(id)
    return deets

def get_current_doctors(id):
    docsdeet = db.session.query(Doctor).get(id)
    return docsdeet


# @app.route('/api/protected_route', methods=['GET'])
# @jwt_required()
# @api_login_required(expected_role=None)
# def protected_route():
#     print('done')
#     current_user = get_jwt_identity()
#     print('done again')
#     return jsonify({"message": f"Welcome, user {current_user['id']}!"}), 200


#forgot password ...............
# s = URLSafeTimedSerializer(app.secret_key)  

# def generate_password_reset_token(email):  
#     return s.dumps(email, salt='password-reset-salt')

@app.route('/chatmedium/')
def video():
    return render_template('videoapp.html')

@app.route('/telemed/')
def telemed():
    return render_template('telemed.html',title='Telemed')

# work on the routes...APPOINTMENT BOOKING................
@app.route('/appointment/')  
def appointment():  
   
    return render_template('appointment_info.html')


@app.route('/schedule', methods=['POST'])
def schedule():
    data = request.get_json()
    new_appointment = Appointment(
        summary=data['summary'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        patient_email=data['patient_email'],
        patient_name=data['patient_name']
    )
    
    db.session.add(new_appointment)
    db.session.commit()
    
    return jsonify({'link': f'/appointment/{new_appointment.id}'}) 




@app.route('/success/')  
def success():  
    return "Appointment successfully scheduled!" 
# ........APPOINTMEnT END..........................

# ........doctors availabilty start..........................

@app.route('/availability/', methods=['GET', 'POST'])  
def availability():  
    if request.method == 'POST':  
        # Handle form submission  
        specialty = request.form.get('specialty')  
        location = request.form.get('location')  
        gender = request.form.getlist('gender')  
        language = request.form.getlist('language')  
        date = request.form.get('date')  
        time = request.form.get('time')  

        # Here you would typically process the data and query your database  
        return render_template('doc_availability.html', specialty=specialty, location=location, gender=gender, language=language, date=date, time=time)  

    return render_template('doc_availability.html')  


# ........patients route start..........................

@app.route('/patients_landing/')
def patients():
    id = session.get('user_online')
    user=db.session.query(PersonalDetail).get(id)
    return render_template('patients.html',user=user)


@app.route('/vcsignup/')
def vcsignup():
    return render_template('virtual_signup.html',title='V|singup')

# @app.route('/vcsignin/',methods=['GET','POST'])
# def vcsignin():
#     if request.method =='GET':
#         return render_template('virtual_signin.html',title='V|singin')
#     else:
#         email = request.form.get('email')
#         password = request.form.get('password')

        
#         if email == '' or password == '':
#             flash('Both fields must be supplied',category='error')
#             return redirect('/vcsignin/')
#         else:
#             user=db.session.query(User).filter(User.email==email).first()
#             docs=db.session.query(Doctor).filter(Doctor.email==email).first()
#             if user != None:
#                 stored_hash = user.password #get hashed password from database
#                 chk = check_password_hash(stored_hash,password)
#                 if chk == True: #login was successfull
#                     #return user object as response...............
#                     flash('Logged in successfully!',category='success')
#                     session['user_online'] = user.id
#                     return redirect(url_for('patients'))
#                 else:
#                     flash('Invalid password',category='error')
#             else:
#                 flash('Invalid email',category='error')
#             # doctor side...............................
#             if docs != None:
#                 stored_hash = docs.password #get hashed password from database
#                 chk = check_password_hash(stored_hash,password)
#                 if chk == True: #login was successfull
#                     #return doc object as response............
#                     flash('Logged in successfully!',category='success')
#                     session['user_online'] = docs.id
#                     return redirect(url_for('doctor_page'))
#                 else:
#                     flash('Invalid password',category='error')
#             else:
#                 flash('Invalid email',category='error')
 

#             return redirect('/vcsignin/')

@app.route('/vcsignin/', methods=['GET', 'POST'])
def vcsignin():
    if request.method == 'GET':
        return render_template('virtual_signin.html', title='V|singin')
    else:
        email = request.form.get('email')
        password = request.form.get('password')

        if email == '' or password == '':
            flash('Both fields must be supplied', category='error')
            return redirect('/vcsignin/')
        else:
            user = db.session.query(User).filter(User.email == email).first()
            docs = db.session.query(Doctor).filter(Doctor.email == email).first()
            if user is not None:
                stored_hash = user.password  # get hashed password from database
                chk = check_password_hash(stored_hash, password)
                if chk:  # login was successful
                    flash('Logged in successfully!', category='success')
                    session['user_online'] = user.id
                    # Create JWT token
                    access_token = create_access_token(identity={'id': user.id, 'role': 'patient'})
                    return redirect(url_for('patients'))

                    # return jsonify({"message": "Logged in successfully!", "token": access_token}), 200
                else:
                    flash('Invalid password', category='error')
            else:
                flash('Invalid email', category='error')
            # doctor side
            if docs is not None:
                stored_hash = docs.password  # get hashed password from database
                chk = check_password_hash(stored_hash, password)
                if chk:  # login was successful
                    flash('Logged in successfully!', category='success')
                    session['user_online'] = docs.id
                    # Create JWT token
                    access_token = create_access_token(identity={'id': docs.id, 'role': 'doctor'})
                    return redirect(url_for('doctor_page'))
                    # return jsonify({"message": "Logged in successfully!", "token": access_token}), 200
                else:
                    flash('Invalid password', category='error')
            else:
                flash('Invalid email', category='error')

            return redirect('/vcsignin/')


#.........................................

#...................    API SECTION     ......................

@app.route('/api/telemed/', methods=['GET'])
def api_telemed():
    return jsonify({"message": "Telemed page"}), 200

@app.route('/api/appointment/', methods=['GET'])
def api_appointment():
    return jsonify({"message": "Appointment info page"}), 200

@app.route('/api/schedule', methods=['POST'])
def api_schedule():
    data = request.get_json()
    new_appointment = Appointment(
        summary=data['summary'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        patient_email=data['patient_email'],
        patient_name=data['patient_name']
    )
    
    db.session.add(new_appointment)
    db.session.commit()
    
    return jsonify({'link': f'/appointment/{new_appointment.id}'}), 201

@app.route('/api/success/', methods=['GET'])
def api_success():
    return jsonify({"message": "Appointment successfully scheduled!"}), 200

@app.route('/api/availability/', methods=['GET', 'POST'])
def api_availability():
    if request.method == 'POST':
        specialty = request.json.get('specialty')
        location = request.json.get('location')
        gender = request.json.get('gender')
        language = request.json.get('language')
        date = request.json.get('date')
        time = request.json.get('time')

        # Here you would typically process the data and query your database
        return jsonify({
            "specialty": specialty,
            "location": location,
            "gender": gender,
            "language": language,
            "date": date,
            "time": time
        }), 200

    return jsonify({"message": "GET request for availability"}), 200

@app.route('/api/patients_landing/', methods=['GET'])
@api_login_required(roles_required=['patient'])  # Protect the route with the decorator
def api_patients():
    id = session.get('user_online')
    user = db.session.query(PersonalDetail).get(id)
    if user:
        return jsonify({
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email
        }), 200
    return jsonify({"error": "User  not found"}), 404

@app.route('/api/vcsignup/', methods=['GET'])
def api_vcsignup():
    return jsonify({"message": "Virtual signup page"}), 200

# @app.route('/api/vcsignin/', methods=['POST'])
# @csrf.exempt
# def api_vcsignin():
#     email = request.json.get('email')
#     password = request.json.get('password')

#     if not email or not password:
#         return jsonify({"error": "Both fields must be supplied"}), 400

#     user = db.session.query(User).filter(User.email == email).first()
#     docs = db.session.query(Doctor).filter(Doctor.email == email).first()

#     if user:
#         stored_hash = user.password
#         if check_password_hash(stored_hash, password):
#             session['user_online'] = user.id
#             return jsonify({"message": "Logged in successfully!", "role": "patient"}), 200
#         else:
#             return jsonify({"error": "Invalid password"}), 401

#     if docs:
#         stored_hash = docs.password
#         if check_password_hash(stored_hash, password):
#             session['user_online'] = docs.id
#             return jsonify({"message": "Logged in successfully!", "role": "doctor"}), 200
#         else:
#             return jsonify({"error": "Invalid password"}), 401

#     return jsonify({"error": "Invalid email"}), 404

@app.route('/api/vcsignin/', methods=['POST'])
@csrf.exempt
def api_vcsignin():
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({"error": "Both fields must be supplied"}), 400

    user = db.session.query(User).filter(User.email == email).first()
    docs = db.session.query(Doctor).filter(Doctor.email == email).first()

    if user:
        stored_hash = user.password
        if check_password_hash(stored_hash, password):
            session['user_online'] = user.id
            access_token = jwt.encode({'id': user.id, 'role': 'patient'}, key=os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
            return jsonify({"message": "Logged in successfully!", "token": access_token}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401

    if docs:
        stored_hash = docs.password
        if check_password_hash(stored_hash, password):
            session['user_online'] = docs.id
            access_token = jwt.encode({'id': docs.id, 'role': 'doctor'}, key=os.getenv('JWT_SECRET_KEY'), algorithm='HS256')
            return jsonify({"message": "Logged in successfully!", "token": access_token}), 200
        else:
            return jsonify({"error": "Invalid password"}), 401

    return jsonify({"error": "Invalid email"}), 404

@app.route('/api/vpersonal/', methods=['POST'])
@csrf.exempt
def api_vpersonal():
    id = session.get('user_online')
    userdeets = get_user_by_id(id)

    if request.method == 'POST':
        full_name = request.json.get('fullName')
        date_of_birth = request.json.get('dateOfBirth')
        gender = request.json.get('gender')
        address = request.json.get('address')
        zip_code = request.json.get('zipCode')
        phone_number = request.json.get('phoneNumber')
        email = request.json.get('email')

        personal_detail = PersonalDetail(
            full_name=full_name,
            date_of_birth=date_of_birth,
            gender=gender,
            address=address,
            zip_code=zip_code,
            phone_number =phone_number,
            email=email,
            user_id=id
        )

        db.session.add(personal_detail)
        db.session.commit()
        return jsonify({"message": "Personal details saved successfully!"}), 201

    return jsonify({"error": "GET request for personal details"}), 200

@app.route('/api/vhealth/', methods=['POST'])
@csrf.exempt
def api_vhealth():
    user_id = session.get('user_online')

    if request.method == 'POST':
        allergies = request.json.get('allergies', False)
        chronic_illness = request.json.get('chronicIllness', False)
        previous_surgeries = request.json.get('previousSurgeries', False)
        medications = request.json.get('medications', False)
        family_medical_history = request.json.get('familyMedicalHistory', False)
        other_conditions = request.json.get('otherConditions', False)
        reason_for_consultation = request.json.get('consultation_reason')

        health_history = HealthHistory(
            user_id=user_id,
            allergies=allergies,
            chronic_illness=chronic_illness,
            previous_surgeries=previous_surgeries,
            medications=medications,
            family_medical_history=family_medical_history,
            other_conditions=other_conditions,
            reason_for_consultation=reason_for_consultation
        )

        db.session.add(health_history)
        db.session.commit()
        return jsonify({"message": "Health history saved successfully!"}), 201

    return jsonify({"error": "GET request for health history"}), 200

@app.route('/api/vinsurance/', methods=['POST'])
@csrf.exempt
def api_vinsurance():
    user_id = session.get('user_online')

    if request.method == 'POST':
        insurance_provider = request.json.get('insuranceProvider')
        policy_number = request.json.get('policyNumber')
        dob = request.json.get('dob')
        gender = request.json.get('gender')

        insurance_info = InsuranceInfo(
            user_id=user_id,
            insurance_provider=insurance_provider,
            policy_number=policy_number,
            dob=dob,
            gender=gender
        )

        db.session.add(insurance_info)
        db.session.commit()
        return jsonify({"message": "Insurance information saved successfully!"}), 201

    return jsonify({"error": "GET request for insurance information"}), 200

@app.route('/api/vmedical/', methods=['GET'])
def api_vmedical():
    return jsonify({"message": "Medical content page"}), 200

@app.route('/api/submit/', methods=['POST']) #this route is for signing up
@csrf.exempt
def api_submit():
    email = request.json.get('email')
    pwd = request.json.get('password')
    role = request.json.get('role')

    if not email or not pwd or not role:
        return jsonify({"message": "All fields are required", "status": "missing_field"}), 400

    hashed = generate_password_hash(pwd)

    user = db.session.query(User).filter(User.email == email).first()
    doctor = db.session.query(Doctor).filter(Doctor.email == email).first()

    if user or doctor:
        return jsonify({"message": "Email already exists", "status": "user_exists_already!"}), 400

    if role == 'doctor':
        new_user = Doctor(email=email, password=hashed)
        redirect_url = url_for('doc_s1')
    elif role == 'patient':
        new_user = User(email=email, password=hashed)
        redirect_url = url_for('vpersonal')
    else:
        return jsonify({"message": "Invalid role selected", "status": "invalid_role"}), 400

    db.session.add(new_user)
    db.session.commit()
    session['user_online'] = new_user.id

    return jsonify({
        "message": f"{role.capitalize()} registered successfully!",
        "status": "success",
        "redirect_url": redirect_url
    }), 200

@app.route('/api/doc_search/', methods=['POST'])
@csrf.exempt
def api_doc_search():
    search_query = request.json.get('search_query', '')
    doctors = []

    doctors_info = DoctorInformation.query.filter(
        DoctorInformation.full_name.like(f'%{search_query}%')
    ).all()

    for info in doctors_info:
        doctors.append({
            'full_name': info.full_name,
            'doctor_id': info.doctor_id
        })

    return jsonify(doctors), 200

@app.route('/api/doctor/', methods=['GET'])
@api_login_required(roles_required=['doctor'])  # Protect the route with the decorator
def api_doctor_page():
    id = session.get('cust_online')
    doc_online = db.session.query(PersonalDetail).get(id)

    if doc_online:
        return jsonify({
            "id": doc_online.id,
            "full_name": doc_online.full_name,
            "email": doc_online.email
        }), 200

    return jsonify({"error": "Doctor not found"}), 404

@app.route('/api/changedp/', methods=['POST'])
@login_required
def api_change_dp():
    id = session.get('user_online')
    doc = db.session.query(Doctor).filter(Doctor.id == id).first()

    if request.method == 'POST':
        dp = request.files.get('dp')
        if dp:
            filename = dp.filename
            allowed = ['jpg', 'png', 'jpeg']
            ext = filename.split('.')[-1]

            if ext in allowed:
                newname = secrets.token_hex(10) + '.' + ext
                dp.save('pkg/static/doctors/' + newname)

                doc.doc_pix = newname
                db.session.commit()
                return jsonify({"message": "Profile picture uploaded successfully!"}), 200
            else:
                return jsonify({"error": "File extension not allowed, allowed extensions are jpg, png, jpeg"}), 400
        else:
            return jsonify({"error": "You need to select a file for upload"}), 400

    return jsonify({"error": "GET request for changing profile picture"}), 200

@app.route('/api/doc_s1/', methods=['POST'])
@csrf.exempt
@api_login_required(roles_required=['doctor'])  # Protect the route with the decorator
def api_doc_s1():
    if request.method == 'POST':
        full_name = request.json.get('fullName')
        bio = request.json.get('bio')
        phone_number = request.json.get('phone')
        email = request.json.get('email')
        dob = request.json.get('dob')
        gender = request.json.get('gender')
        address = request.json.get('address')
        zip_code = request.json.get('zip')

        doctor_info = DoctorInformation(
            full_name=full_name,
            bio=bio,
            phone_number=phone_number,
            email=email,
            dob=datetime.strptime(dob, '%d/%m/%Y').date(),
            gender=gender,
            address=address,
            zip_code=zip_code,
            doctor_id=session['user_online']
        )

        db.session.add(doctor_info)
        db.session.commit()
        return jsonify({"message": "Doctor information saved successfully!"}), 201

    return jsonify({"error": "GET request for doctor step 1"}), 200

@app.route('/api/doc_s2/', methods=['POST'])
@csrf.exempt
@api_login_required(roles_required=['doctor'])  # Protect the route with the decorator
def api_doc_s2():
    if request.method == 'POST':
        hospital_name = request.json.get('hospitalName')
        title = request.json.get('title')
        specialty = request.json.get('specialty')
        language = request.json.get('language')
        years_of_experience = request.json.get('experience')
        opening_time = request.json.get('openingTime')
        closing_time = request.json.get('closingTime')

        doctor_medhistory = DoctorMedhistory(
            hospital_name=hospital_name,
            title=title,
            specialty=specialty,
            language=language,
            years_of_experience=years_of_experience,
            opening_time=datetime.strptime(opening_time, '%H:%M').time() if opening_time else None,
            closing_time=datetime.strptime(closing_time, '%H:%M').time() if closing_time else None,
            doctor_id=session['user_online']
        )

        db.session.add(doctor_medhistory)
        db.session.commit()
        return jsonify({"message": "Doctor medical history saved successfully!"}), 201

    return jsonify({"error": "GET request for doctor step 2"}), 200

@app.route('/api/doc_s3/', methods=['POST'])
@csrf.exempt
@api_login_required(roles_required=['doctor'])  # Protect the route with the decorator
def api_doc_s3():
    if request.method == 'POST':
        institution_name = request.json.get('institutionName')
        year_received = request.json.get('yearReceived')
        credential_id = request.json.get('credentialId')

        year_received_date = None
        if year_received and year_received.isdigit() and len(year_received) == 4:
            year_received_date = datetime.strptime(year_received, '%Y').date()
        else:
            return jsonify({"error": "Please enter a valid year (YYYY)."}), 400

        doctor_license = DoctorLicense(
            institution_name=institution_name,
            year_received=year_received_date,
            credential_id=credential_id,
            doctor_id=session['user_online']
        )

        db.session.add(doctor_license)
        db.session.commit()
        return jsonify({"message": "Doctor license information saved successfully!"}), 201

    return jsonify({"error": "GET request for doctor step 3"}), 200

@app.route('/api/cholera/', methods=['GET'])
def api_cholera():
    return jsonify({"message": "Cholera information page"}), 200

@app.route('/api/mpox/', methods=['GET'])
def api_mpox():
    return jsonify({"message": "Mpox information page"}), 200

@app.route('/api/donate/', methods=['POST'])
@csrf.exempt
def api_donate():
    if request.method == 'POST':
        donor_name = request.json.get('name')
        donor_email = request.json.get('email')
        donor_phone = request.json.get('phone')
        subject = request.json.get('subject')
        amount = request.json.get('amount')
        card_number = request.json.get('card-number')
        expiry_date = request.json.get('expiry-date')
        cvv = request.json.get('cvv')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", donor_email):
            return jsonify({'error': 'Invalid email address!'}), 400

        new_donation = Donation(
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            subject=subject,
            amount=amount,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv
        )

        db.session.add(new_donation)
        db.session.commit()

        return jsonify({'message': f'Thank you for your donation, {donor_name}! We appreciate your support.'}), 201

    return jsonify({"error": "GET request for donation"}), 200

@app.route('/api/partners/', methods=['POST'])
@csrf.exempt
def api_partners():
    if request.method == 'POST':
        user_name = request.json.get('name')
        user_email = request.json.get('email')
        user_phone = request.json.get('phone')
        message = request.json.get('message')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            return jsonify({'error': 'Invalid email address!'}), 400

        new_partnership = Partnership(
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            message=message
        )

        db.session.add(new_partnership)
        db.session.commit()

        return jsonify({'message': 'Thank you for your partnership request!'}), 201

    return jsonify({"error": "GET request for partnership"}), 200

@app.route('/api/volunteer_dash/', methods=['GET'])
def api_volunteer_dash():
    return jsonify({"message": "Volunteer dashboard page"}), 200

@app.route('/api/volunteer_opportunity/', methods=['GET'])
def api_volunteer_opportunity():
    return jsonify({"message": "Volunteer opportunity page"}), 200

@app.route('/api/volunteer_status/', methods=['GET'])
def api_volunteer_status():
    return jsonify({"message": "Volunteer status page"}), 200

@app.route('/api/volunteer_profile/', methods=['GET'])
def api_volunteer_profile():
    return jsonify({"message": "Volunteer profile page"}), 200

@app.route('/api/volunteer_setting/', methods=['GET'])
def api_volunteer_setting():
    return jsonify({"message": "Volunteer settings page"}), 200

@app.route('/api/submit_volunteer/', methods=['POST'])
@csrf.exempt
def api_submit_volunteer():
    if request.method == 'POST':
        volunteer_name = request.json.get('fullname')
        volunteer_email = request.json.get('email')
        volunteer_phone = request.json.get('phone')
        skills_description = request.json.get('subject')
        message = request.json.get('message')

        if not re.match(r"[^@]+@[^@]+\.[^@]+", volunteer_email):
            return jsonify({'error': 'Invalid email address!'}), 400

        new_volunteer = Volunteer(
            volunteer_name=volunteer_name,
            volunteer_email=volunteer_email,
            volunteer_phone=volunteer_phone,
            skills_description=skills_description,
            message=message
        )

        db.session.add(new_volunteer)
        db.session.commit()

        return jsonify({'message': f'Thank you for signing up, {volunteer_name}! We will contact you soon.'}), 201

    return jsonify({"error": "GET request for volunteer submission"}), 200

@app.route('/api/vsignup1/', methods=['GET'])
def api_vsignup1():
    return jsonify({"message": "Virtual signup step 1 page"}), 200

@app.route('/api/vsignup2/', methods=['GET'])
def api_vsignup2():
    return jsonify({"message": "Virtual signup step 2 page"}), 200

@app.route('/api/vsignup3/', methods=['GET'])
def api_vsignup3():
    return jsonify({"message": "Virtual signup step 3 page"}), 200

@app.route('/api/thank_you/', methods=['GET'])
def api_thank_you():
    return jsonify({"message": "Thank you page"}), 200

@app.route('/api/patient_info/', methods=['GET'])
def api_patient_info():
    return jsonify({"message": "Patient info page"}), 200

@app.route('/api/doc_info/<int:id>', methods=['GET'])
def api_doc_info(id):
    doctors = db.session.query(DoctorInformation).filter(DoctorInformation.doctor_id == id).first()
    if doctors:
        return jsonify({
            "id": doctors.doctor_id,
            "full_name": doctors.full_name,
            "specialty": doctors.specialty
        }), 200
    return jsonify({"error": "Doctor not found"}), 404
#...................    API SECTION END     ......................



#.........................................
@app.route('/vpersonal/', methods=['GET', 'POST'])
def vpersonal():
    id = session.get('user_online')

    userdeets = get_user_by_id(id)
    if request.method == 'POST':
        full_name = request.form['fullName']
        date_of_birth = request.form['dateOfBirth']
        gender = request.form['gender']
        address = request.form['address']
        zip_code = request.form['zipCode']
        phone_number = request.form['phoneNumber']
        email = request.form['email']
        
        # Ensure user_id is set
        user_id = id  # Use the session ID or however you retrieve the user ID

        # Insert into database
        personal_detail = PersonalDetail(full_name=full_name,
                                         date_of_birth=date_of_birth,
                                         gender=gender,
                                         address=address,
                                         zip_code=zip_code,
                                         phone_number=phone_number,
                                         email=email,
                                         user_id=user_id)  # Set the user_id

        db.session.add(personal_detail)
        db.session.commit()
        return redirect(url_for('vhealth'))  # Redirect to the next form (Health History)

    return render_template('personal_details.html',userdeets=userdeets, title='Personal Details')


@app.route('/vhealth/', methods=['GET', 'POST'])
def vhealth():
    user_id = session.get('user_online')  # Retrieve the user ID from the session

    if request.method == 'POST':
        # Extracting the form data
        allergies = request.form.get('allergies', False) == 'on'  # Checkboxes return 'on' if checked
        chronic_illness = request.form.get('chronicIllness', False) == 'on'
        previous_surgeries = request.form.get('previousSurgeries', False) == 'on'
        medications = request.form.get('medications', False) == 'on'
        family_medical_history = request.form.get('familyMedicalHistory', False) == 'on'
        other_conditions = request.form.get('otherConditions', False) == 'on'
        reason_for_consultation = request.form['consultation_reason']  # Ensure this matches your form

        # Insert into database
        health_history = HealthHistory(
            user_id=user_id,  # Set the user_id
            allergies=allergies,
            chronic_illness=chronic_illness,
            previous_surgeries=previous_surgeries,
            medications=medications,
            family_medical_history=family_medical_history,
            other_conditions=other_conditions,
            reason_for_consultation=reason_for_consultation  # Use the correct field name
        )
        
        db.session.add(health_history)
        db.session.commit()
        return redirect(url_for('vinsurance'))  # Redirect to the next form (Insurance Info)

    return render_template('health_history.html', title='Health History')


@app.route('/vinsurance/', methods=['GET', 'POST'])
def vinsurance():
    user_id = session.get('user_online')  # Retrieve the user ID from the session

    if request.method == 'POST':
        # Extracting the form data
        insurance_provider = request.form['insuranceProvider']
        policy_number = request.form['policyNumber']
        dob = request.form['dob']
        gender = request.form['gender']
        
        # Insert into database
        insurance_info = InsuranceInfo(
            user_id=user_id,  # Associate with the logged-in user
            insurance_provider=insurance_provider,
            policy_number=policy_number,
            dob=dob,
            gender=gender
        )
        
        db.session.add(insurance_info)
        db.session.commit()
        return redirect('/vcsignin/')  # Redirect after form completion

    return render_template('insurance_info.html', title='Insurance Information')




@app.route('/vmedical/')
def vmedical():
    return render_template('medical_content.html',title='Medical|content')


@app.route('/submit/', methods=['POST'])
def submit():
    if request.method == 'POST':
        email = request.form.get('email')
        pwd = request.form.get('password')
        role = request.form.get('role')

    # Validate input fields
    if not email or not pwd or not role:
        return jsonify({"message": "All fields are required", "status": "missing_field"}), 400

    if pwd.strip() == '':
        return jsonify({"message": "Password cannot be empty", "status": "empty_password"}), 400

    # Hash the password
    hashed = generate_password_hash(pwd)

    # Check if the email already exists
    user = db.session.query(User).filter(User.email == email).first()
    doctor = db.session.query(Doctor).filter(Doctor.email == email).first()
    # volunteer = db.session.query(Volunteer).filter(Volunteer.email == email).first()
    
    if user or doctor:  # or volunteer...should be added to this
        return jsonify({"message": "Email already exists", "status": "user_exists_already!"}), 400

    # Create a new user based on their role
    if role == 'doctor':
        new_user = Doctor(email=email, password=hashed)
        redirect_url = url_for('doc_s1')  # Redirect to /doc_s1/ for doctors
    elif role == 'patient':
        new_user = User(email=email, password=hashed)
        redirect_url = url_for('vpersonal')  # Redirect to /vpersonal/ for patients
    # elif role == 'volunteer':
    #     new_user = Volunteer(email=email, password=hashed)
    #     redirect_url = url_for('volunteer_route')  # Redirect to a specific route for volunteers
    else:
        return jsonify({"message": "Invalid role selected", "status": "invalid_role"}), 400

    # Add the user to the session and database
    db.session.add(new_user)
    db.session.commit()

    # Set session for the user
    session['user_online'] = new_user.id

    # Return the appropriate redirect URL based on the role
    return jsonify({
        "message": f"{role.capitalize()} registered successfully!",
        "status": "success",
        "redirect_url": redirect_url
    }), 200



@app.route('/doc_search/', methods=['GET', 'POST'])
def doc_search():
    doctors = []  # Initialize an empty list for doctors
    if request.method == 'POST':  
        search_query = request.form['search_query']  
        
        # Querying the DoctorInformation and DoctorMedhistory tables
        doctors_info = DoctorInformation.query.filter(
            DoctorInformation.full_name.like(f'%{search_query}%')
        ).all()
        
        doctors_medhistory = DoctorMedhistory.query.filter(
            (DoctorMedhistory.hospital_name.like(f'%{search_query}%')) |
            (DoctorMedhistory.specialty.like(f'%{search_query}%'))
        ).all()

        # Combine results
        for info in doctors_info:
            # Find corresponding med history
            med_history = DoctorMedhistory.query.filter_by(doctor_id=info.doctor_id).first()
            if med_history:
                doctors.append({
                    'full_name': info.full_name,
                    'hospital_name': med_history.hospital_name,
                    'specialty': med_history.specialty,
                    'doctor_id': info.doctor_id  # You can use this for further actions
                })

        # Also include doctors found by specialty
        for med in doctors_medhistory:
            if med.doctor_id not in [doc['doctor_id'] for doc in doctors]:  # Avoid duplicates
                doctor_info = DoctorInformation.query.filter_by(doctor_id=med.doctor_id).first()
                if doctor_info:
                    doctors.append({
                        'full_name': doctor_info.full_name,
                        'hospital_name': med.hospital_name,
                        'specialty': med.specialty,
                        'doctor_id': med.doctor_id
                    })

        # Debugging: Print the search query and results
        print(f"Search Query: {search_query}")
        print(f"Doctors Found: {doctors}")

    return render_template('doc_search.html', doctors=doctors, title='Search | Doctor')

@app.route('/doctor/')  
def doctor_page():
    id = session.get('cust_online')
    doc_online=db.session.query(PersonalDetail).get(id)

    return render_template('doctors.html', doc_online=doc_online) 



#-------------CHANGE DP START----------------------------------
@app.route('/changedp/',methods=['POST','GET'])
@login_required
def change_dp():
    id = session.get('user_online')
    # user_id = get_user_by_id(id)
    doc=db.session.query(Doctor).filter(Doctor.id==id).first()


    
    if request.method=='POST':
        dp=request.files.get('dp')
        
        filename=dp.filename #getting the img name
        allowed=['jpg','png','jpeg','JPG','PNG','JPEG']
        dp_deets=filename.split('.')
        ext=dp_deets[-1]

        if filename:
            if ext in allowed:
                newname = secrets.token_hex(10)+ '.' +ext
                dp.save('pkg/static/doctors/' + newname )

                doc.doc_pix=newname
                db.session.commit()
                flash('profile picture uploaded successfully!',category='success')
                return redirect('/doc_dashboard/')
            else:
                flash('file extension not allowed,allowed extension(jpg,png,jpeg)',category="error") 
                return redirect('/doc_dashboard/')
        else:
            flash('You need to select a file for upload and provide title',category='warn')
            return redirect('/doc_dashboard/')
        

    return redirect('/doc_dashboard/')





@app.route('/doc_s1/', methods=['GET', 'POST'])
def doc_s1():
    if request.method == 'POST':
        # Collect data from the form
        full_name = request.form.get('fullName')
        bio = request.form.get('bio')
        phone_number = request.form.get('phone')
        email = request.form.get('email')
        dob = request.form.get('dob')
        gender = request.form.get('gender')
        address = request.form.get('address')
        zip_code = request.form.get('zip')

        # Create a new DoctorInformation instance
        doctor_info = DoctorInformation(
            full_name=full_name,
            bio=bio,
            phone_number=phone_number,
            email=email,
            dob=datetime.strptime(dob, '%d/%m/%Y').date(),
            gender=gender,
            address=address,
            zip_code=zip_code,
            doctor_id=session['user_online']  # Assuming the doctor_id is stored in the session
        )

        # Add to the database
        db.session.add(doctor_info)
        db.session.commit()

        # Redirect to the next step
        return redirect(url_for('doc_s2'))

    return render_template('doc_s1.html')  # Render the first form page

@app.route('/doc_s2/', methods=['GET', 'POST'])
def doc_s2():
    if request.method == 'POST':
        # Collect data from the form
        hospital_name = request.form.get('hospitalName')
        title = request.form.get('title')
        specialty = request.form.get('specialty')
        language = request.form.get('language')
        years_of_experience = request.form.get('experience')
        opening_time = request.form.get('openingTime')
        closing_time = request.form.get('closingTime')

         # Create a new DoctorMedhistory instance
        doctor_medhistory = DoctorMedhistory(
            hospital_name=hospital_name,
            title=title,
            specialty=specialty,
            language=language,
            years_of_experience=years_of_experience,
            opening_time = datetime.strptime(opening_time, '%H:%M').time() if opening_time else None,
            closing_time = datetime.strptime(closing_time, '%H:%M').time() if closing_time else None,
            doctor_id=session['user_online']  # Assuming the doctor_id is stored in the session
        )

        # Add to the database
        db.session.add(doctor_medhistory)
        db.session.commit()

        # Redirect to the next step
        return redirect(url_for('doc_s3'))

    return render_template('doc_s2.html')  # Render the second form page



@app.route('/doc_s3/', methods=['GET', 'POST'])
def doc_s3():
    if request.method == 'POST':
        # Collect data from the form
        institution_name = request.form.get('institutionName')
        year_received = request.form.get('yearReceived')
        credential_id = request.form.get('credentialId')

        # Validate and convert year_received
        year_received_date = None
        if year_received and year_received.isdigit() and len(year_received) == 4:
            year_received_date = datetime.strptime(year_received, '%Y').date()
        else:
            flash("Please enter a valid year (YYYY).")  # Flash an error message
            return redirect(url_for('doc_s3'))  # Redirect back to the form

        # Create a new DoctorLicense instance
        doctor_license = DoctorLicense(
            institution_name=institution_name,
            year_received=year_received_date,
            credential_id=credential_id,
            doctor_id=session['user_online']  # Assuming the doctor_id is stored in the session
        )

        # Add to the database
        db.session.add(doctor_license)
        db.session.commit()

        # Redirect to a confirmation page or dashboard
        return redirect(url_for('doctor_page'))

    return render_template('doc_s3.html')


@app.route('/cholera/')
def cholera():
    return render_template('cholera.html')

@app.route('/mpox/')
def mpox():
    return render_template('mpox.html')


@app.route('/donate/', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donor_name = request.form['name']
        donor_email = request.form['email']
        donor_phone = request.form['phone']
        subject = request.form.get('subject')  # Optional
        amount = request.form['amount']
        card_number = request.form['card-number']
        expiry_date = request.form['expiry-date']
        cvv = request.form['cvv']

        # Simple validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", donor_email):
            flash('Invalid email address!', 'danger')
            return render_template('donate.html')  # Adjust to your donation page template

        # Here you would typically process the payment using a payment gateway.
        # For demonstration purposes, we will just save the donation info.

        new_donation = Donation(
            donor_name=donor_name,
            donor_email=donor_email,
            donor_phone=donor_phone,
            subject=subject,
            amount=amount,
            card_number=card_number,
            expiry_date=expiry_date,
            cvv=cvv
        )

        db.session.add(new_donation)
        db.session.commit()

        flash('Thank you for your donation, {}! We appreciate your support.'.format(donor_name), 'success')
        return redirect(url_for('thank_you'))  # Redirect to a thank you page or another page after submission

    return render_template('donate.html')  # Render the donation form for GET requests




# Route for the Partners page

@app.route('/partners/', methods=['GET', 'POST'])
def partners():
    if request.method == 'POST':
        user_name = request.form['name']
        user_email = request.form['email']
        user_phone = request.form['phone']
        message = request.form.get('message')  # Optional

        # Simple validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_email):
            flash('Invalid email address!', 'danger')
            return render_template('contact.html')  # Adjust to your contact page template

        # Create a new partnership record
        new_partnership = Partnership(
            user_name=user_name,
            user_email=user_email,
            user_phone=user_phone,
            message=message
        )
        
        db.session.add(new_partnership)
        db.session.commit()

        flash('Thank you for your partnership request!', 'success')
        return redirect(url_for('thank_you'))  # Redirect to a thank you page or another page after submission

    return render_template('partners.html')  # Render the contact form for GET requests
# # Route for the Volunteer page

@app.route('/volunteer_dash/')
def volunteer_dash():
    return render_template('volunteer.html',title='volunteer|Dash')

@app.route('/volunteer_opportunity/')
def volunteer_opportunity():
    return render_template('vol_opportunity.html',title='volunteer|Dash')

@app.route('/volunteer_status/')
def volunteer_status():
    return render_template('vol_status.html',title='volunteer|Dash')

@app.route('/volunteer_profile/')
def volunteer_profile():
    return render_template('vol_profile.html',title='volunteer|Dash')

@app.route('/volunteer_setting/')
def volunteer_setting():
    return render_template('vol_settings.html',title='volunteer|Dash')




@app.route('/submit_volunteer/', methods=['GET', 'POST'])  
def submit_volunteer():  
    if request.method == 'POST':
        volunteer_name = request.form['fullname']
        volunteer_email = request.form['email']
        volunteer_phone = request.form['phone']
        skills_description = request.form['subject']  # What they are good at
        message = request.form.get('message')  # Optional

        # Simple validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", volunteer_email):
            flash('Invalid email address!', 'danger')
            return render_template('volunteer.html')  # Adjust to your volunteer page template

        # Create a new volunteer record
        new_volunteer = Volunteer(
            volunteer_name=volunteer_name,
            volunteer_email=volunteer_email,
            volunteer_phone=volunteer_phone,
            skills_description=skills_description,
            message=message
        )
        
        db.session.add(new_volunteer)
        db.session.commit()

        flash('Thank you for signing up, {}! We will contact you soon.'.format(volunteer_name), 'success')
        return redirect(url_for('index'))  # Redirect to a thank you page or another page after submission

    return render_template('volunteer.html')  # Render the volunteer form for GET requests

@app.route('/vsignup1/')
def vsignup1():
    return render_template('vsignup1.html')


@app.route('/vsignup2/')
def vsignup2():
    return render_template('vsignup2.html')


@app.route('/vsignup3/')
def vsignup3():
    return render_template('vsignup3.html')






@app.route('/thank_you/')
def thank_you():
    return render_template('thank_you.html')

@app.route('/patient_info/', methods=['GET'])
def patient_info():
    return render_template('patient_info.html')

      
@app.route('/doc_info/<int:id>')
def doc_info(id):
    doctors = db.session.query(DoctorInformation).filter(DoctorInformation.doctor_id==id)

    return render_template('doc_info.html',title='doc|info', doctors=doctors)






