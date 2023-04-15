import os
from dotenv import load_dotenv
import pandas as pd
from typing import List
from datetime import datetime
from catboost import CatBoostClassifier
from fastapi import Depends, FastAPI
from schema import PostGet
from loguru import logger
from sqlalchemy import create_engine


load_dotenv(r'.env')

POSTGRESUSER = os.environ['POSTGRESUSER']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = os.environ['POSTGRES_PORT']
POSTGRES_DATABASE = os.environ['POSTGRES_DATABASE']

str_con_db = f'postgresql://{POSTGRESUSER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'

engine = create_engine(str_con_db, pool_size=5, max_overflow=5)


def batch_load_sql(query: str, CHUNKSIZE: int = 1000000, engine=engine) -> pd.DataFrame:
    """Выполнение sql-запроса query и выгрузка результата, по чанкам."""
    conn = engine.connect().execution_options(stream_results=True)
    chunks = []
    for chunk_dataframe in pd.read_sql(query, conn, chunksize=CHUNKSIZE):
        chunks.append(chunk_dataframe)
    conn.close()
    return pd.concat(chunks, ignore_index=True)


def get_model_path(path: str) -> str:
    if os.environ.get("IS_LMS") == "1":  # проверяем где выполняется код в лмс, или локально. Немного магии
        MODEL_PATH = '/workdir/user_input/model'
    else:
        MODEL_PATH = path
    return MODEL_PATH


def load_models():
    model_path = get_model_path("catboost_model_6_github")
    model = CatBoostClassifier()
    model.load_model(model_path)
    return model


def load_features_post() -> pd.DataFrame:
    df_post_data = batch_load_sql("""SELECT * FROM pavel55645_posts_info_lesson_22""")
    df_post_data = df_post_data.drop(['index'], axis=1)
    return df_post_data


def load_features_user() -> pd.DataFrame:
    df_user_data = batch_load_sql("""SELECT * FROM pavel55645_users_lesson_22""")
    df_user_data = df_user_data.drop(['index'], axis=1)
    return df_user_data


def load_liked_posts() -> pd.DataFrame:
    liked_posts_query = """
        SELECT distinct post_id, user_id
        FROM public.feed_data
        WHERE action='like'
        """
    liked_posts = batch_load_sql(liked_posts_query)
    return liked_posts


logger.info("start")
logger.info("loading model")
model = load_models()

logger.info("loading post features")
df_post_data = load_features_post()

logger.info("loading user features")
df_user_data = load_features_user()

logger.info("loading liked posts")
liked_posts = load_liked_posts()

logger.info("service is up and running") 

app = FastAPI()

def get_recommended_feed(
        id: int, time: datetime, limit: int,
        df_post_data: pd.DataFrame = df_post_data,
        df_user_data: pd.DataFrame = df_user_data,
        liked_posts: pd.DataFrame = liked_posts,
        model=model):
    
    # Выбираем sel_posts с каждого топика
    sel_posts = 100
    
    logger.info(f"user_id: {id}")
    df_user_id = df_user_data.loc[df_user_data.user_id == id]
    df_user_id = df_user_id.drop('user_id', axis=1)
    
    # Определяем категории постов, где пользователь поставил наибольшее число лайков
    user_topic = df_user_id[['business', 'covid', 'entertainment', 'movie', 'politics', 'sport', 'tech']]
    #print(user_topic)
    user_topic = user_topic.iloc[0]
    
    user_topic = user_topic.sort_values(ascending=False).iloc[:3].index.to_list()
    #print(user_topic)
    
    post_ids = []
    for utopic in user_topic:
        ids = df_post_data[df_post_data['topic'] == utopic]['post_id'].iloc[:sel_posts].values
        post_ids.extend(ids)
        
    liked_posts_user = liked_posts[(liked_posts['post_id'].isin(post_ids)) & (liked_posts['user_id'] == id)]
    liked_posts_ids = liked_posts_user['post_id'].values
    # id шники постов, по которым будет вычислено предсказание
    post_ids = list(set(post_ids) - set(liked_posts_ids))
    #print(post_ids)
    
    # посты, по которым будет вычислено предсказание
    logger.info("post columns")
    post_candidate = df_post_data[df_post_data.post_id.isin(post_ids)]
    posts_features = post_candidate.drop(['text'], axis=1)
    content = post_candidate[['post_id', 'text', 'topic']]
    
    logger.info("zipping everything")
    add_user_features = dict(zip(df_user_id.columns, df_user_id.values[0]))
    
    logger.info("assigning everything")
    user_posts_features = posts_features.assign(**add_user_features)
    user_posts_features = user_posts_features.set_index('post_id')
    
    logger.info("add time info")
    user_posts_features['hour'] = time.hour
    user_posts_features['month'] = time.month
    
    logger.info("predicting")
    #print(user_posts_features.columns)
    
    predicts = model.predict_proba(user_posts_features)[:, 1]
    user_posts_features["predicts"] = predicts
    
    logger.info("deleting liked posts")
    liked_posts_ = liked_posts[liked_posts.user_id == id].post_id.values
    filtered_ = user_posts_features[~user_posts_features.index.isin(liked_posts_)]
    recomended_posts = filtered_.sort_values('predicts')[-limit:].index
    
    return [
        PostGet(**{"id": i,
                   "text": content[content.post_id == i].text.values[0],
                   "topic": content[content.post_id == i].topic.values[0]})
        for i in recomended_posts
    ]


@app.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(id: int, time: datetime, limit: int = 10) -> List[PostGet]:
    return get_recommended_feed(id, time, limit)

