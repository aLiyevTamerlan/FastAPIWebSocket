from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserInfo(BaseModel):
    id: int
    username: str
    role: str = "user"

class Message(BaseModel):
    user_id: int
    message: str