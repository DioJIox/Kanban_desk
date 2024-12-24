from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import engine, Base, get_db
from models import User, Project, KanbanColumn, Task, TaskLog
from schemas import UserCreate, ProjectCreate, ColumnCreate, TaskCreate, TaskLogCreate
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()

Base.metadata.create_all(bind=engine)

security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials, db: Session):
    user = db.query(User).filter(User.email == credentials.username).first()
    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

@app.get("/protected-route")
def protected_route(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = authenticate_user(credentials, db)
    return {"message": f"Sucsessful, {user.email}"}

@app.post("/users/", response_model=UserCreate)
async def create_user(user: UserCreate, db: Session =
 Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/users/{user_id}", response_model=UserCreate)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user

@app.get("/users/", response_model=List[UserCreate])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/projects/", response_model=ProjectCreate)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    new_project = Project(name=project.name)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.get("/projects/", response_model=List[ProjectCreate])
def get_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()

@app.post("/columns/")
async def create_column(column: ColumnCreate, db: Session = Depends(get_db)):
    new_column = KanbanColumn(name=column.name, project_id=column.project_id)
    db.add(new_column)
    db.commit()
    db.refresh(new_column)
    return new_column

@app.get("/columns/{project_id}/", response_model=List[ColumnCreate])
def get_columns_by_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db.query(KanbanColumn).filter(KanbanColumn.project_id == project_id).all()

@app.post("/tasks/", response_model=TaskCreate)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    column = db.query(KanbanColumn).filter(KanbanColumn.id == task.column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    new_task = Task(title=task.title, description=task.description, column_id=task.column_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    log = TaskLog(task_id=new_task.id, action="Task created", timestamp=datetime.now())
    db.add(log)
    db.commit()
    return new_task

@app.get("/tasks/{column_id}/", response_model=List[TaskCreate])
def get_tasks_by_column(column_id: int, db: Session = Depends(get_db), order: str = "asc"):
    column = db.query(KanbanColumn).filter(KanbanColumn.id == column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found")
    query = db.query(Task).filter(Task.column_id == column_id)
    if order == "asc":
        query = query.order_by(Task.created_at.asc())
    elif order == "desc":
        query = query.order_by(Task.created_at.desc())
    return query.all()

@app.get("/logs/{task_id}/", response_model=List[TaskLogCreate])
def get_task_logs(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db.query(TaskLog).filter(TaskLog.task_id == task_id).all()
