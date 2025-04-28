from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import string
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Patient, Session, Reading
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Connect to database
engine = create_engine('sqlite:///robot_monitoring.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


# Helper function to generate random patient ID
def generate_patient_id(length=6):
    letters = string.ascii_uppercase
    numbers = string.digits
    # Generate ID with format: LETTER-NUMBER-LETTER-NUMBER (e.g., A1B2C3)
    result = ''.join(random.choice(letters) + random.choice(numbers) for _ in range(length // 2))
    return result


# Convert database objects to dictionaries
def patient_to_dict(patient):
    return {
        'id': patient.id,
        'name': patient.name
    }


def session_to_dict(session):
    return {
        'id': session.id,
        'patient_id': session.patient_id,
        'start_time': session.start_time.isoformat(),
        'planned_duration': session.planned_duration,
        'actual_duration': session.actual_duration,
        'completed': session.completed
    }


def reading_to_dict(reading):
    return {
        'id': reading.id,
        'session_id': reading.session_id,
        'timestamp': reading.timestamp.isoformat(),
        'temperature': reading.temperature,
        'blood_leakage': reading.blood_leakage
    }


# API Routes
@app.route('/api/patients', methods=['GET'])
def get_patients():
    db_session = DBSession()
    patients = db_session.query(Patient).all()
    result = [patient_to_dict(patient) for patient in patients]
    db_session.close()
    return jsonify(result)


@app.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    db_session = DBSession()
    patient = db_session.query(Patient).filter_by(id=patient_id).first()
    if not patient:
        db_session.close()
        return jsonify({'error': 'Patient not found'}), 404
    result = patient_to_dict(patient)
    db_session.close()
    return jsonify(result)


@app.route('/api/patients', methods=['POST'])
def create_patient():
    data = request.json
    db_session = DBSession()

    # Generate unique ID if not provided
    if 'id' not in data or not data['id']:
        # Generate ID and ensure it's unique
        while True:
            new_id = generate_patient_id()
            existing = db_session.query(Patient).filter_by(id=new_id).first()
            if not existing:
                break
        data['id'] = new_id

    # Create new patient
    new_patient = Patient(id=data['id'], name=data['name'])
    db_session.add(new_patient)
    db_session.commit()

    result = patient_to_dict(new_patient)
    db_session.close()
    return jsonify(result), 201


@app.route('/api/patients/<patient_id>/sessions', methods=['GET'])
def get_patient_sessions(patient_id):
    db_session = DBSession()
    sessions = db_session.query(Session).filter_by(patient_id=patient_id).order_by(desc(Session.start_time)).all()
    result = [session_to_dict(session) for session in sessions]
    db_session.close()
    return jsonify(result)


@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    db_session = DBSession()
    session = db_session.query(Session).filter_by(id=session_id).first()
    if not session:
        db_session.close()
        return jsonify({'error': 'Session not found'}), 404
    result = session_to_dict(session)
    db_session.close()
    return jsonify(result)


@app.route('/api/sessions/<int:session_id>/readings', methods=['GET'])
def get_session_readings(session_id):
    db_session = DBSession()
    readings = db_session.query(Reading).filter_by(session_id=session_id).order_by(Reading.timestamp).all()
    result = [reading_to_dict(reading) for reading in readings]
    db_session.close()
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5000)