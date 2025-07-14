from datetime import datetime
from pkg import db
# User model updates based on form data
class User(db.Model):  
    __tablename__ = 'users'  
    
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(255), nullable=False)  
   
    # Relationships
    health_history = db.relationship('HealthHistory', back_populates='user', uselist=False)  # One-to-One relationship
    insurance_info = db.relationship('InsuranceInfo', back_populates='user', uselist=False)  # One-to-One relationship
    appointments = db.relationship('Appointment', back_populates='user', lazy=True)  # One-to-Many relationship
    user_person = db.relationship('PersonalDetail', back_populates='person_user', lazy=True)  
    donations = db.relationship('Donation', back_populates='user', lazy=True)  
    partnerships = db.relationship('Partnership', back_populates='user', lazy=True)  
    contact_messages = db.relationship('ContactMessage', back_populates='user', lazy=True)   


# Appointment model
class Appointment(db.Model):  
    __tablename__ = 'appointments'  # Specify the table name
    
    id = db.Column(db.Integer, primary_key=True)  
    patient_name = db.Column(db.String(100), nullable=False)  
    patient_email = db.Column(db.String(120), nullable=False, unique=True)  
    summary = db.Column(db.String(200), nullable=False)  
    start_time = db.Column(db.DateTime, nullable=False)  
    end_time = db.Column(db.DateTime, nullable=False)  
    google_event_id = db.Column(db.String(200), nullable=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Foreign key to Doctor
    user = db.relationship('User', back_populates='appointments')  # Relationship to User

    def __repr__(self):  
        return f'<Appointment {self.summary} - {self.start_time}>'


# Health History Model for the 'health_history' form
class HealthHistory(db.Model):
    __tablename__ = 'health_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to User
    
    allergies = db.Column(db.Boolean, nullable=False, default=False)
    chronic_illness = db.Column(db.Boolean, nullable=False, default=False)
    previous_surgeries = db.Column(db.Boolean, nullable=False, default=False)
    medications = db.Column(db.Boolean, nullable=False, default=False)
    family_medical_history = db.Column(db.Boolean, nullable=False, default=False)
    other_conditions = db.Column(db.Boolean, nullable=False, default=False)
    reason_for_consultation = db.Column(db.Text, nullable=True)  # Reason for consultation

    user = db.relationship('User', back_populates='health_history')

# Insurance Info Model for 'insurance_info' form
class InsuranceInfo(db.Model):
    __tablename__ = 'insurance_info'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Link to User
    
    insurance_provider = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    
    dob = db.Column(db.Date, nullable=False)  # Added date of birth field
    gender = db.Column(db.String(10), nullable=False)  # Added gender field
    coverage_amount = db.Column(db.Float, nullable=True)
    document_url = db.Column(db.String(200), nullable=True)  # Upload document

    user = db.relationship('User', back_populates='insurance_info')


class PersonalDetail(db.Model):
    __tablename__ = 'personal_details'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    person_user = db.relationship('User', back_populates='user_person', lazy=True)  
    
    # Foreign key to link to User  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Added Foreign Key  

# Doctor model for healthcare professionals
class Doctor(db.Model):  
    __tablename__ = 'doctors'  
    
    id = db.Column(db.Integer, primary_key=True)  
    email = db.Column(db.String(120), unique=True, nullable=False) 
    password = db.Column(db.String(255), nullable=False)  
    doc_pix=db.Column(db.String(255), nullable=True) 

    volunteers = db.relationship('Volunteer', back_populates='doctor', lazy=True)  # Relationship to Volunteer  
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    doctor_information = db.relationship('DoctorInformation', backref='info', uselist=False)  # One-to-one relationship

class Donation(db.Model):  
    __tablename__ = 'donations'  
    
    id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    
    donor_name = db.Column(db.String(200), nullable=False)  # Name of the donor
    donor_email = db.Column(db.String(200), nullable=False)  # Email of the donor
    donor_phone = db.Column(db.String(20), nullable=False)   # Phone number of the donor
    subject = db.Column(db.String(255))                      # Optional subject
    amount = db.Column(db.Float, nullable=False)             # Donation amount
    card_number = db.Column(db.String(20), nullable=False)   # Card number
    expiry_date = db.Column(db.String(5), nullable=False)    # Expiry date (MM/YY)
    cvv = db.Column(db.String(4), nullable=False)            # CVV
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of creation
    user = db.relationship('User', back_populates='donations')


    def __repr__(self):
        return f'<Donation {self.donor_name}, Amount: {self.amount}>'


class Volunteer(db.Model):  
    __tablename__ = 'volunteers'  
    
    id = db.Column(db.Integer, primary_key=True)  
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Reference to Doctor  
    volunteer_name = db.Column(db.String(200), nullable=False)  # Name of the volunteer
    volunteer_email = db.Column(db.String(200), nullable=False)  # Email of the volunteer
    volunteer_phone = db.Column(db.String(20), nullable=False)   # Phone number of the volunteer
    skills_description = db.Column(db.String(255), nullable=False)  # Skills description
    message = db.Column(db.Text)  # Optional message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of creation
    doctor = db.relationship('Doctor', back_populates='volunteers')  # Relationship to Doctor


    def __repr__(self):
        return f'<Volunteer {self.volunteer_name}>'


class Partnership(db.Model):  
    __tablename__ = 'partnerships'  
    
    id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  
    user_name = db.Column(db.String(200), nullable=False)  # Name of the user
    user_email = db.Column(db.String(200), nullable=False)  # Email of the user
    user_phone = db.Column(db.String(20), nullable=False)   # Phone number of the user
    message = db.Column(db.Text)                             # Optional message
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of creation
    user = db.relationship('User', back_populates='partnerships')


    def __repr__(self):
        return f'<Partnership {self.user_name}>'
    
class ContactMessage(db.Model):  
    __tablename__ = 'contact_messages'  
    
    id = db.Column(db.Integer, primary_key=True)  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  
    subject = db.Column(db.String(200), nullable=False)  
    message = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  
    user = db.relationship('User', back_populates='contact_messages')  


class Project(db.Model):  
    __tablename__ = 'projects'  
    
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(200), nullable=False)  
    description = db.Column(db.Text, nullable=False)  
    impact_metrics = db.Column(db.Text, nullable=True)  
    image_url = db.Column(db.String(200), nullable=True)  

class BlogPost(db.Model):  
    __tablename__ = 'blog_posts'  
    
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(200), nullable=False)  
    excerpt = db.Column(db.Text, nullable=False)  
    content = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  

class PodcastEpisode(db.Model):  
    __tablename__ = 'podcast_episodes'  
    
    id = db.Column(db.Integer, primary_key=True)  
    title = db.Column(db.String(200), nullable=False)  
    description = db.Column(db.Text, nullable=False)  
    audio_url = db.Column(db.String(200), nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  


class DoctorInformation(db.Model):
    __tablename__ = 'doctor_information'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Reference to Doctor
    full_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', backref='doctor_info', uselist=False)#one to one


class DoctorMedhistory(db.Model):
    __tablename__ = 'doctor_medhistory'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Reference to Doctor
    hospital_name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer, nullable=False)
    opening_time = db.Column(db.Time, nullable=False)
    closing_time = db.Column(db.Time, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', backref='doctor_medhistory')

    

class DoctorLicense(db.Model):
    __tablename__ = 'doctor_license'
    
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)  # Reference to Doctor
    institution_name = db.Column(db.String(255), nullable=False)
    year_received = db.Column(db.Date, nullable=True)
    credential_id = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor = db.relationship('Doctor', backref='doctor_license')
