# schemas.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Any, Dict
from uuid import UUID

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = "STUDENT"

class UserCreate(UserBase):
    password: str # This will be hashed before storing

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # Allows Pydantic to read from ORM models

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: UUID

class TokenData(BaseModel):
    id: Optional[UUID] = None
    role: Optional[str] = None

# --- Exam Schemas ---
class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    duration_minutes: int
    start_time: datetime
    end_time: datetime

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class Exam(ExamBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    questions: List["Question"] = [] # Relationship to questions

    class Config:
        from_attributes = True

# --- Exam Assignment Schemas ---
class ExamAssignmentBase(BaseModel):
    student_id: UUID
    exam_id: UUID

class ExamAssignmentCreate(ExamAssignmentBase):
    pass

class ExamAssignment(ExamAssignmentBase):
    id: UUID
    status: str
    assigned_at: datetime
    started_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    student: User # Nested User schema
    exam: Exam # Nested Exam schema

    class Config:
        from_attributes = True

# --- Session Schemas ---
class SessionBase(BaseModel):
    student_id: UUID
    exam_id: UUID

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: UUID
    start_time: datetime
    end_time: Optional[datetime] = None
    final_risk_score: int
    
    class Config:
        from_attributes = True

# --- ProctorEvent Schemas ---
class ProctorEventBase(BaseModel):
    session_id: UUID
    ts: datetime
    type: str
    details_json: Optional[Dict[str, Any]] = None # Use Dict[str, Any] for dynamic JSON
    risk_delta: int
    snapshot_url: Optional[str] = None

class ProctorEventCreate(ProctorEventBase):
    pass

class ProctorEvent(ProctorEventBase):
    id: UUID
    
    class Config:
        from_attributes = True

# --- RiskTick Schemas (New) ---
class RiskTickBase(BaseModel):
    session_id: UUID
    ts: datetime
    risk_score: int

class RiskTickCreate(RiskTickBase):
    pass

class RiskTick(RiskTickBase):
    id: UUID

    class Config:
        from_attributes = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    exam_id: UUID
    question_text: str
    question_type: Optional[str] = "MULTIPLE_CHOICE"
    options_json: Optional[Dict[str, Any]] = None # Use Dict for JSON objects
    correct_answer_json: Optional[Dict[str, Any]] = None # Use Dict for JSON objects
    points: Optional[int] = 1

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options_json: Optional[Dict[str, Any]] = None
    correct_answer_json: Optional[Dict[str, Any]] = None
    points: Optional[int] = None

class Question(QuestionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Session Report Schema (New) ---
class SessionReport(BaseModel):
    session_id: UUID
    exam_id: UUID
    exam_title: str
    student_id: UUID
    student_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    final_risk_score: int
    proctor_events: List[ProctorEvent]
    risk_ticks: List[RiskTick]
    event_summary: Dict[str, int] # e.g., {"face_away": 5, "multiple_faces": 1}

    class Config:
        from_attributes = True

# Forward references for circular dependencies in Pydantic
# This resolves issues where schemas reference each other (e.g., Exam references Question)
Exam.model_rebuild()
ExamAssignment.model_rebuild()
