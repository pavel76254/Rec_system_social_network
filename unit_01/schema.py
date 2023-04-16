from pydantic import BaseModel
from datetime import datetime


class UserGet(BaseModel):
    id: int
    age: int
    city: str
    country: str
    exp_group: int
    gender: int
    os: str
    source: str
    
    class Config:
        orm_mode = True


class PostGet(BaseModel):
    id: int
    text: str
    topic: str
    
    class Config:
        orm_mode = True
        

class FeedGet(BaseModel):
    post_id: int
    post: PostGet
    user_id: int
    user: UserGet
    action: str
    time: datetime
    
    class Config:
        orm_mode = True
