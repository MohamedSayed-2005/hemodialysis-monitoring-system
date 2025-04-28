from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Patient, Session, Reading
import datetime

engine = create_engine('sqlite:///robot_monitoring.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Query all sessions
print("All Sessions:")
sessions = session.query(Session).all()
for s in sessions:
    print(f"Session ID: {s.id}, Patient ID: {s.patient_id}, Duration: {s.planned_duration / 60} minutes")
    print(f"  Start Time: {s.start_time}, Completed: {s.completed}")

    # Get readings for this session
    readings = session.query(Reading).filter_by(session_id=s.id).all()
    print(f"  Number of readings: {len(readings)}")

    # Show last 3 readings
    if readings:
        print("  Recent readings:")
        for reading in readings[-3:]:
            print(f"    Time: {reading.timestamp}, Temp: {reading.temperature}, Blood Leakage: {reading.blood_leakage}")

    print("")

session.close()