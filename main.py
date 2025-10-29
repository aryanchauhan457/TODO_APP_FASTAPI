from fastapi import FastAPI, status, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Simple FastAPI App")

# ✅ Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] if you host it there
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("NOW")
try:
    conn = psycopg2.connect(host='127.0.0.1', database='postgres', user='postgres', password='aryan', cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    print("Database connection successful.")
    
except Exception as e:
    print(e)
print("END")


tasks = [
    {"id": 1, "title": "First", "description": "first task", "status": "pending"},
    {"id": 2, "title": "Second", "description": "Second task", "status": "complete"},
    {"id": 3, "title": "Third", "description": "Third task", "status": "pending"},
]

class DATA(BaseModel):
    title: str
    description: Optional[str]
    status: str = "pending"
    
class TASK(BaseModel):
    id: int
    title: Optional[str]
    description: Optional[str]
    status: Optional[str]
    
class ID(BaseModel):
    id: int

@app.get("/tasks/", status_code=status.HTTP_200_OK)
def get_all_tasks():
    cursor.execute("""SELECT * FROM test""")
    my_tasks = cursor.fetchall()
    # print("get:", my_tasks)
    
    return {"tasks": my_tasks}

@app.post("/create/", status_code=status.HTTP_201_CREATED)
def create_task(task: DATA):
    
    cursor.execute("""INSERT INTO test (title, description, status) VALUES (%s, %s, %s) RETURNING *""", (task.title, task.description, task.status))
    new_task = cursor.fetchone()
    conn.commit()
    print(new_task)
    
    # task_dict = {
    #     "id": max(task["id"] for task in tasks) + 1 if tasks else 1,
    #     "title": task.title,
    #     "description": task.description,
    #     "status": task.status,
    # }
    # tasks.append(task_dict)
    return {"task added": new_task}

@app.put("/update/", status_code=status.HTTP_200_OK)
def uptade_task(task: TASK):
    cursor.execute("""UPDATE test SET title = %s, description = %s, status = %s WHERE id = %s RETURNING *""",
                   (task.title, task.description, task.status, task.id))
        
    updated_task = cursor.fetchone()
    conn.commit()
    # for i, taskk in enumerate(tasks):
    #     if taskk["id"] == task.id:
            
    #         updated_task = {
    #             "id": task.id,
    #             "title": task.title,
    #             "description": task.description,
    #             "status": task.status
    #         }
    #         tasks[i] = updated_task
            # return {"task updated": updated_task}
    if updated_task:
        return {"task updated": updated_task}
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, headers={"error":f"ID {task.id} not found."}, detail=("The entered id not found in the database."))

@app.delete("/delete/")
def delete_task(id: ID):
    id = id.id
    # for i, taskk in enumerate(tasks):
    #     if taskk["id"] == id:
    #         tasks.pop(i)
    #         return Response(
    #             status_code=status.HTTP_204_NO_CONTENT,
    #             headers={"X-Message": f"Task with ID {id} has been deleted."}
    #         )
    cursor.execute("""DELETE FROM test WHERE id = %s RETURNING *""", (str(id)))
    deleted_task = cursor.fetchone()
    conn.commit()
    
    if deleted_task:
        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
            headers={"X-Message": f"Task with ID {id} has been deleted."}
        )
    
    # Also fix this one (same problem)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with ID {id} not found in the database."
    )
