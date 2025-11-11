# fast.py (أو main.py)

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union
import json
import os
import asyncio
import logging

# Import database, models, schemas, and crud using absolute imports (without '.')
from backend.database import engine, Base, get_db
from backend.models import User, Exam, ExamAssignment, Session as DBSession, ProctorEvent, RiskTick, Question
from schemas import (
    UserCreate, User, Token, ExamCreate, Exam, ExamUpdate, ExamAssignmentCreate, ExamAssignment, 
    SessionCreate, Session as SchemaSession, ProctorEventCreate, ProctorEvent, 
    QuestionCreate, Question, QuestionUpdate, SessionReport, RiskTickCreate
)
from backend.crud import (
    get_user, create_user, get_user_by_email, get_users, delete_user, 
    create_exam, get_exam, get_exams, update_exam, delete_exam, 
    create_exam_assignment, get_exam_assignments_by_student, start_exam_assignment, submit_exam_assignment, 
    create_session, get_session, end_session, create_proctor_event, get_proctor_events_by_session, 
    get_active_assignment, create_exam_question, get_questions_by_exam, get_question, update_question, delete_question, 
    update_session_risk_score, create_risk_tick, get_risk_ticks_by_session
)


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced AI Exam Monitoring System API",
    description="API for managing students, exams, and real-time proctoring data.",
    version="2.0.0"
)

# --- Database Initialization (wrapped in try-except for better error visibility) ---
try:
    logger.info("Attempting to create database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully or already exist.")
except Exception as e:
    logger.critical(f"FATAL ERROR during database table creation: {e}", exc_info=True)
    # Raise an exception to prevent the application from starting if DB init fails
    raise RuntimeError(f"Failed to initialize database: {e}. Please check your database.py, models.py, and permissions.")

# Configure CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2PasswordBearer for handling token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Health Check Endpoint (NEW) ---
@app.get("/health", summary="Health check endpoint", response_model=Dict[str, str])
async def health_check():
    """
    Returns a simple status to indicate if the FastAPI application is running.
    Does not interact with the database.
    """
    return {"status": "ok", "message": "FastAPI is running!"}


# --- Security Functions ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return plain_password == hashed_password

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return f"mock_jwt_token_{json.dumps(to_encode)}"

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        if not token.startswith("mock_jwt_token_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data_str = token.replace("mock_jwt_token_", "")
        token_data = json.loads(token_data_str)
        user_id = token_data.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = crud.get_user(db, user_id=user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (JSON decoding error)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication",
        )

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can perform this action"
        )
    return current_user

# --- Authentication Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "user_id": str(user.id)}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- User Management Endpoints (Admin Only) ---

@app.post("/users/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user.password_hash = user.password # Temporary for testing
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=User)
def read_user(user_id: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    success = crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return

# --- Exam Management Endpoints (Admin Only) ---

@app.post("/exams/", response_model=Exam, status_code=status.HTTP_201_CREATED)
def create_exam(exam: ExamCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    return crud.create_exam(db=db, exam=exam)

@app.get("/exams/", response_model=List[Exam])
def read_exams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exams = crud.get_exams(db, skip=skip, limit=limit)
    return exams

@app.get("/exams/{exam_id}", response_model=Exam)
def read_exam(exam_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_exam = crud.get_exam(db, exam_id=exam_id)
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return db_exam

@app.put("/exams/{exam_id}", response_model=Exam)
def update_exam(exam_id: str, exam: ExamUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_exam = crud.update_exam(db, exam_id=exam_id, exam=exam)
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return db_exam

@app.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    success = crud.delete_exam(db, exam_id=exam_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return

# --- Exam Assignment Endpoints (Admin Only) ---

@app.post("/assignments/", response_model=ExamAssignment)
def assign_exam(assignment: ExamAssignmentCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_assignment = crud.create_exam_assignment(db, assignment=assignment)
    if db_assignment is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create assignment (e.g., student or exam not found, or already assigned)")
    return db_assignment

@app.get("/assignments/student/{student_id}", response_model=List[ExamAssignment])
def get_student_assignments(student_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if str(user.id) != student_id and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view these assignments")
    assignments = crud.get_exam_assignments_by_student(db, student_id=student_id)
    return assignments

@app.put("/assignments/{assignment_id}/start", response_model=ExamAssignment)
def start_exam_assignment(assignment_id: str, db: Session = Depends(get_db), student: User = Depends(get_current_user)):
    db_assignment = crud.start_exam_assignment(db, assignment_id=assignment_id)
    if db_assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or already started/submitted")
    if str(db_assignment.student_id) != str(student.id) and student.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to start this exam")
    return db_assignment

@app.put("/assignments/{assignment_id}/submit", response_model=ExamAssignment)
def submit_exam_assignment(assignment_id: str, db: Session = Depends(get_db), student: User = Depends(get_current_user)):
    db_assignment = crud.submit_exam_assignment(db, assignment_id=assignment_id)
    if db_assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found or not in a suitable state to submit")
    if str(db_assignment.student_id) != str(student.id) and student.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit this exam")
    return db_assignment

# --- Session Management & Proctoring Events ---

@app.post("/sessions/", response_model=SchemaSession)
def create_session(session: SessionCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if str(user.id) != str(session.student_id) and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create session for this student")
    
    assignment = crud.get_active_assignment(db, student_id=session.student_id, exam_id=session.exam_id)
    if not assignment or assignment.status != "STARTED":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No active or started assignment found for this student and exam.")

    return crud.create_session(db=db, session=session)

@app.put("/sessions/{session_id}/end", response_model=SchemaSession)
def end_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if str(db_session.student_id) != str(user.id) and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to end this session")

    return crud.end_session(db, session_id=session_id)

@app.post("/proctor_events/", response_model=ProctorEvent)
def create_proctor_event(event: ProctorEventCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_session = crud.get_session(db, session_id=event.session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found for this event")
    
    if str(db_session.student_id) != str(user.id) and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to post events to this session")

    return crud.create_proctor_event(db=db, event=event)

@app.get("/sessions/{session_id}/events/", response_model=List[ProctorEvent])
def get_proctor_events_for_session(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if str(db_session.student_id) != str(user.id) and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view events for this session")

    events = crud.get_proctor_events_by_session(db, session_id=session_id)
    return events

# --- WebSocket for Real-time Monitoring ---

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        logger.info("ConnectionManager initialized.")

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session: {session_id}. Total connections for session: {len(self.active_connections[session_id])}")

    def disconnect(self, websocket: WebSocket, session_id: str):
        if session_id in self.active_connections:
            try:
                self.active_connections[session_id].remove(websocket)
                if not self.active_connections[session_id]:
                    del self.active_connections[session_id]
                logger.info(f"WebSocket disconnected for session: {session_id}. Remaining connections for session: {len(self.active_connections.get(session_id, []))}")
            except ValueError:
                logger.warning(f"WebSocket not found in active connections for session {session_id} during disconnect.")
        else:
            logger.warning(f"Session ID {session_id} not found in active connections during disconnect.")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, session_id: str, message: str):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(message)
                except RuntimeError as e:
                    logger.error(f"Error sending message to WebSocket for session {session_id}: {e}")
        else:
            logger.warning(f"No active connections for session ID {session_id} to broadcast message.")


manager = ConnectionManager()

@app.websocket("/ws/proctoring/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(websocket, session_id)


@app.post("/proctor_updates/{session_id}")
async def receive_proctor_update(session_id: str, update_data: Dict[str, Any], db: Session = Depends(get_db)):
    logger.info(f"Received proctor update for session {session_id}: {update_data}")
    
    event_type = update_data.get("type", "generic_update")
    risk_delta = update_data.get("risk_delta", 0)
    details = update_data.get("details", {})
    snapshot_url = update_data.get("snapshot_url")
    
    try:
        event_create = ProctorEventCreate(
            session_id=session_id,
            ts=datetime.now(),
            type=event_type,
            details_json=details,
            risk_delta=risk_delta,
            snapshot_url=snapshot_url
        )
        crud.create_proctor_event(db, event=event_create)
        logger.info(f"Proctor event '{event_type}' saved for session {session_id}.")
        
        current_session = crud.get_session(db, session_id=session_id)
        if current_session:
            new_risk_score = current_session.final_risk_score + risk_delta
            crud.update_session_risk_score(db, session_id=session_id, new_score=new_risk_score)
            logger.info(f"Session {session_id} risk score updated to {new_risk_score}")
            
            risk_tick_create = RiskTickCreate(
                session_id=session_id,
                ts=datetime.now(),
                risk_score=new_risk_score
            )
            crud.create_risk_tick(db, risk_tick=risk_tick_create)
            logger.info(f"Risk tick recorded for session {session_id} with score {new_risk_score}")

    except Exception as e:
        logger.error(f"Failed to save proctor event or update session for session {session_id}: {e}")
    
    await manager.broadcast(session_id, json.dumps(update_data))
    return {"message": "Update received and broadcasted."}


# --- Question Management Endpoints (Admin Only) ---

@app.post("/exams/{exam_id}/questions/", response_model=Question)
def create_question_for_exam(exam_id: str, question: QuestionCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_exam = crud.get_exam(db, exam_id=exam_id)
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return crud.create_exam_question(db=db, question=question, exam_id=exam_id)

@app.get("/exams/{exam_id}/questions/", response_model=List[Question])
def read_questions_for_exam(exam_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_exam = crud.get_exam(db, exam_id=exam_id)
    if db_exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    questions = crud.get_questions_by_exam(db, exam_id=exam_id)
    return questions

@app.get("/questions/{question_id}", response_model=Question)
def read_question(question_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_question = crud.get_question(db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return db_question

@app.put("/questions/{question_id}", response_model=Question)
def update_question(question_id: str, question: QuestionUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    db_question = crud.update_question(db, question_id=question_id, question=question)
    if db_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return db_question

@app.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: str, db: Session = Depends(get_db), admin: User = Depends(get_current_admin_user)):
    success = crud.delete_question(db, question_id=question_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return


# --- Session Reporting Endpoints ---

@app.get("/sessions/{session_id}/report/", response_model=SessionReport)
def get_session_report(session_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    if str(db_session.student_id) != str(user.id) and user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this session report")

    exam = crud.get_exam(db, exam_id=db_session.exam_id)
    student = crud.get_user(db, user_id=db_session.student_id)
    proctor_events = crud.get_proctor_events_by_session(db, session_id=session_id)
    risk_ticks = crud.get_risk_ticks_by_session(db, session_id=session_id)

    event_summary = {}
    for event in proctor_events:
        event_summary[event.type] = event_summary.get(event.type, 0) + 1
    
    report_data = SessionReport(
        session_id=str(db_session.id),
        exam_id=str(db_session.exam_id),
        exam_title=exam.title if exam else "N/A",
        student_id=str(db_session.student_id),
        student_name=f"{student.first_name} {student.last_name}" if student else "N/A",
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        final_risk_score=db_session.final_risk_score,
        proctor_events=proctor_events,
        risk_ticks=risk_ticks,
        event_summary=event_summary
    )
    return report_data
