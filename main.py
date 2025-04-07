# main.py
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import datetime
import sqlite3
import hashlib
import jwt
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import whisper
import open_clip
import torch

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
def get_db():
    conn = sqlite3.connect('trimiq.db')
    return conn

# Models
class User(BaseModel):
    username: str
    email: str
    password: str

class UserInDB(User):
    id: int
    balance: float
    minutes_used: float
    ad_revenue: float

# Auth functions
def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Video processing functions
def transcribe_audio(audio_path: str):
    model = whisper.load_model(os.getenv("WHISPER_MODEL"))
    result = model.transcribe(audio_path)
    return result

def match_scenes_with_clip(text: str, video_clips: list):
    model, _, preprocess = open_clip.create_model_and_transforms(
        os.getenv("CLIP_MODEL"),
        pretrained=os.getenv("CLIP_PRETRAINED"))
    tokenizer = open_clip.get_tokenizer(os.getenv("CLIP_MODEL"))
    
    text_tokens = tokenizer([text])
    with torch.no_grad():
        text_features = model.encode_text(text_tokens)
    
    # Implementation for matching video clips to text
    # ...
    return matched_clips

# API Endpoints
@app.post("/register")
async def register(user: User):
    db = get_db()
    cursor = db.cursor()
    
    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    
    # Insert new user
    cursor.execute(
        "INSERT INTO users (username, email, password, balance, minutes_used, ad_revenue) VALUES (?, ?, ?, 0, 0, 0)",
        (user.username, user.email, hashed_password)
    )
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(email: str, password: str):
    db = get_db()
    cursor = db.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
    user = cursor.fetchone()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token_data = {"sub": user[1], "email": user[2]}
    token = create_jwt_token(token_data)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/process-video")
async def process_video(
    background_tasks: BackgroundTasks,
    token: dict = Depends(verify_token),
    audio_file: UploadFile = File(None),
    video_files: list[UploadFile] = File([]),
    text_prompt: str = Form(None),
    resolution: str = Form("720p")
):
    # Check user balance
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT balance FROM users WHERE email = ?", (token["email"],))
    balance = cursor.fetchone()[0]
    
    # Process video
    # 1. Save uploaded files temporarily
    # 2. Transcribe audio if provided
    # 3. Match scenes with video clips or generate from text
    # 4. Edit video with FFmpeg/MoviePy
    # 5. Add transitions, subtitles, noise removal
    # 6. Save final video
    
    # Schedule cleanup
    output_path = f"output/{datetime.datetime.now().timestamp()}.mp4"
    background_tasks.add_task(cleanup_files, output_path)
    
    return {"video_url": output_path, "expires_in": os.getenv("AUTO_DELETE_HOURS")}

def cleanup_files(file_path: str):
    import time
    time.sleep(int(os.getenv("AUTO_DELETE_HOURS")) * 3600)
    if os.path.exists(file_path):
        os.remove(file_path)
