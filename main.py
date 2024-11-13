from typing import List
from sqlalchemy.orm import Session

from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
import os

from database import get_db_session
from managers import ConnectionManager
from schemas import Message, UserCreate, UserInfo
from users.models import User
from utils import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, get_current_user, hash_password
from fastapi.middleware.cors import CORSMiddleware




app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify allowed origins like ["http://127.0.0.1:8000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")


class Token(BaseModel):
    access_token: str
    token_type: str

manager = ConnectionManager()




# WebSocket endpoint for notifications,
@app.websocket("/ws/notifications/{student_id}")
async def websocket_notifications(websocket: WebSocket, student_id: int):
    await manager.connect(student_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Sending a notification to the specified student_id
            await manager.send_personal_message(message=f"New message: {data}", receiver_id=student_id)
    except WebSocketDisconnect:
        manager.disconnect(student_id, websocket)
        await manager.send_personal_message("Bye!!!", receiver_id=student_id)

@app.post("/message")
async def send_message(message: Message):
    await manager.send_personal_message(message = message.message, receiver_id = message.user_id)
    return {"status": "Message sent"}



@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/home", response_class=HTMLResponse)
async def get_home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/register")
async def register(user: UserCreate, db = Depends(get_db_session)):
    # Check if the username already exists
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Hash the password before storing it
    hashed_password = hash_password(user.password)

    # Create the new user
    new_user = User(username=user.username, password=hashed_password, role=user.role)

    # Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully", "user": {"username": new_user.username, "role": new_user.role}}



@app.get("/user", response_model=UserInfo)  # UserCreate is the Pydantic model for user info
async def get_user_info(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role, "id": current_user.id}

@app.get("/users", response_model=List[UserInfo])
def get_all_users(db: Session = Depends(get_db_session)):
    users = db.query(User).all()
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users