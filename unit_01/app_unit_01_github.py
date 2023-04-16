from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func, desc

from database import SessionLocal
from schema import UserGet, PostGet, FeedGet
from table_user import User
from table_post import Post
from table_feed import Feed


app = FastAPI()


def get_db():
    with SessionLocal() as db:
        return db


# Возвращает всю информацию по пользователю с id.
@app.get("/user/{id}", response_model=UserGet)
def get_user_id(id: int, db: Session = Depends(get_db)) -> UserGet:
    result = db.query(User).filter(User.id == id).one_or_none()
    if not result:
        raise HTTPException(404, 'user not found')
    else:
        return result


# Возвращает всю информацию по посту с id.
@app.get("/post/{id}", response_model=PostGet)
def get_post_id(id: int, db: Session = Depends(get_db)) -> PostGet:
    result = db.query(Post).filter(Post.id == id).one_or_none()
    if not result:
        raise HTTPException(404, 'post not found')
    else:
        return result


# Возвращает все действия выполненные над постом с id из Feed.
@app.get("/post/{id}/feed", response_model=List[FeedGet])
def get_feed_post_id(id: int, limit: int = 10, db: Session = Depends(get_db)) -> FeedGet:
    result = db.query(Feed)\
        .filter(Feed.post_id == id)\
        .order_by(Feed.time.desc())\
        .limit(limit)\
        .all()
    if not result:
        raise HTTPException(200, list())
    else:
        return result


# Возвращает все действия пользователя с id из Feed.
@app.get("/user/{id}/feed", response_model=List[FeedGet])
def get_feed_user_id(id: int, limit: int = 10, db: Session = Depends(get_db)) -> FeedGet:
    result = db.query(Feed)\
        .filter(Feed.user_id == id)\
        .order_by(Feed.time.desc())\
        .limit(limit)\
        .all()
    if not result:
        raise HTTPException(200, list())
    else:
        return result


# Возвращает топ limit постов по количеству лайков.
@app.get("/post/recommendations/", response_model=List[PostGet])
def get_recommended(id: int, limit: int = 10, db: Session = Depends(get_db)):
    result = db.query(Post.id, Post.text, Post.topic).select_from(Feed) \
        .join(Post) \
        .filter(Feed.action == 'like') \
        .group_by(Post.id) \
        .order_by(desc(func.count(Post.id))) \
        .limit(limit).all()
    return result
