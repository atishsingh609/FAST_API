import random
from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel #used to validate schema of input data coming to Apis

import psycopg2 # used to connect with postgres
from psycopg2.extras import RealDictCursor
from . import models
from .database import engine, get_db
from sqlalchemy.orm import Session

"""
to start the server use uvicorn main:app
to detect the change and reflect to API USE  uvicorn main:app --reload
"""
app = FastAPI()
my_posts = [{"title": "title of post 1", "content": "content of post 1", "rating": 4, "id": 1},
            {"title": "mu fav pizza", "content": "I love pizza", "rating": 5, "id": 2}]

models.Base.metadata.create_all(bind=engine)
try:
    con = psycopg2.connect(host="localhost", database="fastapi", user="postgres", password="Jaiparshuram@12",
                          cursor_factory = RealDictCursor)
    cursor = con.cursor()
    print("Databse connection is successful")
except Exception as e:
    print("Connecting to Databricks fails due to error ", str(e))



class Post(BaseModel):
    """
    Defined the post schema
    """
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None




@app.get("/")
async def root():
    """
    Here @aap is decorator which make this function as Api.
    async - to implement async call
    get - HTTP method of this API
    ("/") -  This is the path use to hit this function from server url i.e  http://127.0.0.1:8000/
    :return:
    """
    return {"message": "Welcome to my Api!!!"}


@app.get("/posts")
def get_post():
    cursor.execute("""SELECT * from post""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": posts}


# @app.post("/createpost")
# def create_post(payload: dict = Body(...)):
#     """
#     Body reads all data passed through body and convert it to dict and store it to payload .
#     :param payload:
#     :return:
#     """
#     print("Body", payload)
#     return {"message": "Post is create successfully",
#             "data": payload}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    """
    Body reads all data passed through body and convert it to dict and store it to payload .
    :param payload:
    :return:
    """
    # print("Post", post)
    # post_dict = post.dict()
    # post_dict["id"] = random.randrange(0, 1000000)
    # my_posts.append(post_dict)
    cursor.execute("""INSERT into post (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    con.commit()
    return_msg = {"message": "Post is added successfully",
                  "data": new_post}
    return return_msg

@app.get("/post/{id}")
def get_post(id: int):
    requested_post = None
    #
    cursor.execute("""SELECT * from post WHERE id = %s""", (str(id)))
    post = cursor.fetchone()
    if not post:
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"post with id {id} not found"}
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found!!!")
    return {"requested post": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    # post_found = False
    # for i, post in enumerate(my_posts):
    #     if id == post.get("id"):
    #         post_found = True
    #         my_posts.pop(i)
    cursor.execute("""DELETE FROM post WHERE id = %s returning *""", (str(id)))
    deleted_post = cursor.fetchone()
    con.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE post  SET title = %s, content = %s, published = %s WHERE id = %s returning *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    con.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post Not Found !!")
    return {"message": "Update post successfully", "data": updated_post}

"""
SQLALCHEMY Implementations.
"""


@app.get("/sqlalchemy")
def get_posts(db: Session = Depends(get_db)):
    return {"status": "sqlalchemy test done"}