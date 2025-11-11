# models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy_utils import UUIDType
from uuid import uuid4
from datetime import datetime

# Import Base from database.py (now an absolute import)
from backend.database import Base

# --- User Model ---
class User(Base):
    __tablename__ = "users"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False) # In production, this stores a hashed password
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, default="STUDENT") # "ADMIN" or "STUDENT"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exams_assigned = relationship("ExamAssignment", back_populates="student")
    sessions = relationship("Session", back_populates="student")

# --- Exam Model ---
class Exam(Base):
    __tablename__ = "exams"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_to = relationship("ExamAssignment", back_populates="exam")
    sessions = relationship("Session", back_populates="exam")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")


# --- ExamAssignment Model ---
class ExamAssignment(Base):
    __tablename__ = "exam_assignments"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    student_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)
    exam_id = Column(UUIDType(binary=False), ForeignKey("exams.id"), nullable=False)
    status = Column(String, default="PENDING") # PENDING, STARTED, SUBMITTED
    assigned_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="exams_assigned")
    exam = relationship("Exam", back_populates="assigned_to")

# --- Session Model ---
class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    student_id = Column(UUIDType(binary=False), ForeignKey("users.id"), nullable=False)
    exam_id = Column(UUIDType(binary=False), ForeignKey("exams.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True) # Will be set when session ends
    final_risk_score = Column(Integer, default=0) # Aggregated risk score for the entire session
    
    student = relationship("User", back_populates="sessions")
    exam = relationship("Exam", back_populates="sessions")
    proctor_events = relationship("ProctorEvent", back_populates="session", cascade="all, delete-orphan")
    risk_ticks = relationship("RiskTick", back_populates="session", cascade="all, delete-orphan")

# --- ProctorEvent Model ---
class ProctorEvent(Base):
    __tablename__ = "proctor_events"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    session_id = Column(UUIDType(binary=False), ForeignKey("sessions.id"), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, index=True) # Timestamp of the event
    type = Column(String, nullable=False) # e.g., "face_away", "multiple_faces", "suspicious_sound", "browser_tab_change"
    details_json = Column(Text, nullable=True) # JSON string for additional event details
    risk_delta = Column(Integer, default=0) # How much this event impacts the risk score
    snapshot_url = Column(String, nullable=True) # URL to a snapshot image/video of the event

    session = relationship("Session", back_populates="proctor_events")

# --- RiskTick Model (New) ---
class RiskTick(Base):
    __tablename__ = "risk_ticks"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    session_id = Column(UUIDType(binary=False), ForeignKey("sessions.id"), nullable=False)
    ts = Column(DateTime, default=datetime.utcnow, index=True) # Timestamp of the risk score change
    risk_score = Column(Integer, nullable=False) # The cumulative risk score at this timestamp

    session = relationship("Session", back_populates="risk_ticks")

# --- Question Model ---
class Question(Base):
    __tablename__ = "questions"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid4)
    exam_id = Column(UUIDType(binary=False), ForeignKey("exams.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, default="MULTIPLE_CHOICE") # e.g., MULTIPLE_CHOICE, TRUE_FALSE, ESSAY
    options_json = Column(Text, nullable=True) # JSON string for options in MCQs
    correct_answer_json = Column(Text, nullable=True) # JSON string for correct answer(s)
    points = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    exam = relationship("Exam", back_populates="questions")
