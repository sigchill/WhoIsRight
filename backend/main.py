from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlmodel import SQLModel, select, Session
from backend.database import create_db_and_tables, get_session
from backend.models import User
from backend.schemas import UserCreate, UserRead
from backend.auth import get_password_hash, verify_password
from fastapi.middleware.cors import CORSMiddleware

#a polling game where peole have to guess the majroity vote

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/frontend")
def frontend():
    return FileResponse("backend/static/index.html")

polls = {}
submissions = {}
next_poll_id =1 
next_option_id =1
next_submission_id =1

class SubmissionCreate(BaseModel):
    player_name:str
    voted_option_id: int
    predicted_winner_option_id: int
    
class PollCreate(BaseModel):
    question: str
    options: list[str]
    
class VoteCreate(BaseModel):
    option_id: int

@app.get("/")
async def root():
    return {"message":"poll is running"}


#regiser
@app.post("/register", response_model=UserRead, status_code=201)
def register_user(user_data: UserCreate,
                  session: Session = Depends(get_session)
                  ):
    existing_username = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = session.exec( select(User).where(User.email == user_data.email)).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    if len(user_data.password.encode("utf-8"))>72:
        raise HTTPException(status_code=400, detail="password too long")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

#create a poll

@app.post("/polls")
def create_poll(poll:PollCreate):
    global next_poll_id, next_option_id
    
    if(len(poll.options))<2:
        raise HTTPException(status_code=400, detail="poll needs at least 2 otipns")
    poll_id = next_poll_id
    next_poll_id += 1
    
    options = []
    
    for option_text in poll.options:
        option = {
            "id": next_option_id,
            "text": option_text,
            "votes": 0
        }
        options.append(option)
        next_option_id+=1
    polls[poll_id]={
        "id": poll_id,
        "question": poll.question,
        "options":options,
        "is_closed": False,
        "created_at": datetime.now().isoformat()
    }
    return polls[poll_id]
        
        

@app.get("/polls")
def list_polls():
    return list(polls.values())

@app.get("/polls/{poll_id}")
def get_poll(poll_id:int):
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    return polls[poll_id]


@app.post("/polls/{poll_id}/vote")
def vote_poll(poll_id:int, vote_data: VoteCreate):
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    
    poll = polls[poll_id]
    
    if poll["is_closed"]:
        raise HTTPException(status_code=400, detail="poll closed")
    
    for option in poll["options"]:
        if option["id"] == vote_data.option_id:
            option["votes"]+=1
            return{
                "message": "vote counted",
                "poll":poll
            }
    raise HTTPException(status_code=400,detail="option not found")        


#get re'sults of a poll
@app.get("/polls/{poll_id}/results")
def get_results(poll_id:int):
    #if poll_id not in polls:
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    
    poll = polls[poll_id]
    vote_counts = {}
    
    for option in poll["options"]:
        vote_counts[option["id"]] = 0
    
    for submission in submissions.values():
        if submission["poll_id"] == poll_id:
            vote_counts[submission["voted_option_id"]] += 1
    total_votes = sum(vote_counts.values()) 
    
    result_options = []
    for option in poll["options"]:
        result_options.append({
            "id": option["id"],
            "text": option["text"],
            "votes": vote_counts[option["id"]]
        })    
    
    return {
        "poll_id":poll["id"],
        "question": poll["question"],
        "total_votes": total_votes,
        "options": result_options   
    }
    

@app.post("/polls/{poll_id}/submit")
def submit_poll(poll_id:int, submission_data: SubmissionCreate):
   
    global next_submission_id
   
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    
    poll = polls[poll_id]
    
    if polls[poll_id]["is_closed"]:
        raise HTTPException(status_code=400, detail="poll closed")
    
    valid_option_ids = [option["id"] for option in poll["options"]]
    
    if submission_data.voted_option_id not in valid_option_ids:
        raise HTTPException(status_code=400, detail="voted option not found")
   
    if submission_data.predicted_winner_option_id not in valid_option_ids:
        raise HTTPException(status_code=400, detail="predicted winner option not found")
     
    for existing_submission in submissions.values():
        if(
            existing_submission["poll_id"] == poll_id and 
            existing_submission["player_name"] == submission_data.player_name
        ):
            raise HTTPException(status_code=400, detail="player has already submitted for this poll")
            
    
    submission_id = next_submission_id
    next_submission_id += 1
    
    submission = {
        "id": submission_id,
        "player_name": submission_data.player_name,
        "voted_option_id": submission_data.voted_option_id,
        "predicted_winner_option_id": submission_data.predicted_winner_option_id,
        "poll_id": poll_id,
        "submitted_at": datetime.now().isoformat()
    }
    
    submissions[submission_id] = submission
    return {
        "message": "submission recorded",
        "submission": submission
    }

@app.patch("/polls/{poll_id}/close")
def close_poll(poll_id:int):
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    polls[poll_id]["is_closed"] = True
    
    return{
        "message":"poll closed",
        "poll": polls[poll_id]
    }
    
@app.delete("polls/{poll_id}")
def delete_poll(poll_id:int):
    if poll_id not in polls:
        raise HTTPException(status_code=400, detail="poll not found")
    deleted_poll = polls.pop(poll_id)
    
    return{
        "message": "poll deleted",
        "poll": deleted_poll
    }

