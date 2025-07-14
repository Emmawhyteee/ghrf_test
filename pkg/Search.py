from flask import Flask, render_template, request  
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///doctors.db'  
db = SQLAlchemy(app)

class Doctor(db.Model):  
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(100), nullable=False)  
    specialty = db.Column(db.String(100), nullable=False)  
    hospital = db.Column(db.String(100), nullable=False)  
    rating = db.Column(db.Float, nullable=False)  
    description = db.Column(db.Text, nullable=True)

    