# crud.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

# Import models and schemas using absolute imports
import backend.models as models
import schemas

# --- User CRUD Operations ---
def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    # In a real app, hash the password here (e.g., using bcrypt)
    # For now, we are storing plain text for demonstration
    db_user = models.User(
        email=user.email,
        password_hash=user.password, # Temporary: Should be a hashed password
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


# --- Exam CRUD Operations ---
def get_exam(db: Session, exam_id: str):
    return db.query(models.Exam).filter(models.Exam.id == exam_id).first()

def get_exams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Exam).offset(skip).limit(limit).all()

def create_exam(db: Session, exam: schemas.ExamCreate):
    db_exam = models.Exam(**exam.model_dump())
    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)
    return db_exam

def update_exam(db: Session, exam_id: str, exam: schemas.ExamUpdate):
    db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if db_exam:
        for key, value in exam.model_dump(exclude_unset=True).items():
            setattr(db_exam, key, value)
        db.commit()
        db.refresh(db_exam)
    return db_exam

def delete_exam(db: Session, exam_id: str):
    db_exam = db.query(models.Exam).filter(models.Exam.id == exam_id).first()
    if db_exam:
        db.delete(db_exam)
        db.commit()
        return True
    return False


# --- Exam Assignment CRUD Operations ---
def create_exam_assignment(db: Session, assignment: schemas.ExamAssignmentCreate):
    # Check if student and exam exist
    student = db.query(models.User).filter(models.User.id == assignment.student_id).first()
    exam = db.query(models.Exam).filter(models.Exam.id == assignment.exam_id).first()
    if not student or not exam:
        return None # Indicate that student or exam was not found

    # Check if assignment already exists
    existing_assignment = db.query(models.ExamAssignment).filter(
        models.ExamAssignment.student_id == assignment.student_id,
        models.ExamAssignment.exam_id == assignment.exam_id
    ).first()
    if existing_assignment:
        return None # Assignment already exists

    db_assignment = models.ExamAssignment(**assignment.model_dump(), status="PENDING")
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment

def get_exam_assignments_by_student(db: Session, student_id: str):
    return db.query(models.ExamAssignment).filter(models.ExamAssignment.student_id == student_id).all()

def get_active_assignment(db: Session, student_id: str, exam_id: str):
    return db.query(models.ExamAssignment).filter(
        models.ExamAssignment.student_id == student_id,
        models.ExamAssignment.exam_id == exam_id,
        models.ExamAssignment.status == "STARTED" # Only check for STARTED status
    ).first()

def start_exam_assignment(db: Session, assignment_id: str):
    db_assignment = db.query(models.ExamAssignment).filter(models.ExamAssignment.id == assignment_id).first()
    if db_assignment and db_assignment.status == "PENDING":
        db_assignment.status = "STARTED"
        db_assignment.started_at = datetime.utcnow()
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    return None

def submit_exam_assignment(db: Session, assignment_id: str):
    db_assignment = db.query(models.ExamAssignment).filter(models.ExamAssignment.id == assignment_id).first()
    if db_assignment and db_assignment.status == "STARTED":
        db_assignment.status = "SUBMITTED"
        db_assignment.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    return None


# --- Session CRUD Operations ---
def create_session(db: Session, session: schemas.SessionCreate):
    db_session = models.Session(**session.model_dump(), start_time=datetime.utcnow(), final_risk_score=0)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: str):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def end_session(db: Session, session_id: str):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if db_session and db_session.end_time is None: # Only end if not already ended
        db_session.end_time = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
        return db_session
    return None

def update_session_risk_score(db: Session, session_id: str, new_score: int):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if db_session:
        db_session.final_risk_score = new_score
        db.commit()
        db.refresh(db_session)
        return db_session
    return None


# --- Proctor Event CRUD Operations ---
def create_proctor_event(db: Session, event: schemas.ProctorEventCreate):
    # Ensure details_json is stored as a string
    details_json_str = json.dumps(event.details_json) if event.details_json else None
    
    db_event = models.ProctorEvent(
        session_id=event.session_id,
        ts=event.ts,
        type=event.type,
        details_json=details_json_str,
        risk_delta=event.risk_delta,
        snapshot_url=event.snapshot_url
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_proctor_events_by_session(db: Session, session_id: str):
    return db.query(models.ProctorEvent).filter(models.ProctorEvent.session_id == session_id).order_by(models.ProctorEvent.ts).all()

# --- Risk Tick CRUD Operations ---
def create_risk_tick(db: Session, risk_tick: schemas.RiskTickCreate):
    db_risk_tick = models.RiskTick(**risk_tick.model_dump())
    db.add(db_risk_tick)
    db.commit()
    db.refresh(db_risk_tick)
    return db_risk_tick

def get_risk_ticks_by_session(db: Session, session_id: str):
    return db.query(models.RiskTick).filter(models.RiskTick.session_id == session_id).order_by(models.RiskTick.ts).all()


# --- Question CRUD Operations ---
def create_exam_question(db: Session, question: schemas.QuestionCreate, exam_id: str):
    # Ensure options_json and correct_answer_json are stored as strings
    options_json_str = json.dumps(question.options_json) if question.options_json else None
    correct_answer_json_str = json.dumps(question.correct_answer_json) if question.correct_answer_json else None

    db_question = models.Question(
        exam_id=exam_id,
        question_text=question.question_text,
        question_type=question.question_type,
        options_json=options_json_str,
        correct_answer_json=correct_answer_json_str,
        points=question.points
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_question(db: Session, question_id: str):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

def get_questions_by_exam(db: Session, exam_id: str):
    return db.query(models.Question).filter(models.Question.exam_id == exam_id).order_by(models.Question.created_at).all()

def update_question(db: Session, question_id: str, question: schemas.QuestionUpdate):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        update_data = question.model_dump(exclude_unset=True)
        if 'options_json' in update_data:
            update_data['options_json'] = json.dumps(update_data['options_json'])
        if 'correct_answer_json' in update_data:
            update_data['correct_answer_json'] = json.dumps(update_data['correct_answer_json'])
            
        for key, value in update_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: str):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False
