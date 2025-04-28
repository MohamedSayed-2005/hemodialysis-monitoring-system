from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# Set up database connection
engine = create_engine('sqlite:///robot_monitoring.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)


# Define database models
class Patient(Base):
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    sessions = relationship("Session", back_populates="patient")


class Session(Base):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    start_time = Column(DateTime, default=datetime.datetime.now)
    planned_duration = Column(Integer)  # in seconds
    actual_duration = Column(Integer, nullable=True)  # in seconds
    completed = Column(Boolean, default=False)

    patient = relationship("Patient", back_populates="sessions")
    readings = relationship("Reading", back_populates="session")


class Reading(Base):
    __tablename__ = 'readings'

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('sessions.id'))
    timestamp = Column(DateTime, default=datetime.datetime.now)
    temperature = Column(Float, nullable=True)
    blood_leakage = Column(Boolean, default=False)

    session = relationship("Session", back_populates="readings")


# Create tables in the database
Base.metadata.create_all(engine)