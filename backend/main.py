from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/frontend")
def frontend():
    return FileResponse("backend/static/index.html")

polls = {}
next_poll_id =1 
next_option_id =1

class PollCreate(BaseModel):
    question: str
    options: list[str]
    
class VoteCreate(BaseModel):
    option_id: int

@app.get("/")
async def root():
    return {"message":"poll is running"}

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



@app.get("/polls/{poll_id}results")
def get_results(poll_id:int):
    if poll_id not in polls:
        raise HTTPException(status_code=400,detail="poll not found")
    
    poll = polls[poll_id]
    total_votes = sum(option["votes"] for option in poll["options"])
    
    return {
        "poll_id":poll["id"],
        "question": poll["question"],
        "total_votes": total_votes,
        "options": poll["options"]
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

