from sqlmodel import SQLModel

# Schemas for data validation and serialization
class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    
class UserRead(SQLModel):
    id: int
    username: str
    email: str