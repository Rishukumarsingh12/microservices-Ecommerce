from fastapi import FastAPI, Depends, HTTPException
from auth import verify_password, create_access_token
from database import engine, SessionLocal
from models import User
from passlib.context import CryptContext
from database import Base
from schemas import UserCreate, UserResponse, Token, UserLogin
import time
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

app = FastAPI()

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

for i in range(10):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database connected!")
        break
    except OperationalError:
        print("Database not ready... retrying")
        time.sleep(3)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Auth Service Running"}

@app.post("/register", response_model = UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)

    new_user = User(username = user.username, email = user.email, hashed_password = hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    
@app.post("/login", response_model = Token)
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code = 401, detail = "Invalid Email or Password")
    
    access_token = create_access_token(data = {
        "sub": db_user.email,
        "user_id": db_user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }