from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from database import create_db_and_tables, engine
from models import Task
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    with Session(engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

@app.get("/tasks/", response_model=list[Task])
def read_tasks():
    with Session(engine) as session:
        return session.exec(select(Task)).all()

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task.title = updated_task.title
        task.description = updated_task.description
        task.completed = updated_task.completed
        session.commit()
        session.refresh(task)
        return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        session.delete(task)
        session.commit()
        return {"message": "Task deleted"}
