from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    class Config:
        orm_mode = True

class ProjectCreate(BaseModel):
    name: str
    class Config:
        orm_mode = True

class ColumnCreate(BaseModel):
    name: str
    project_id: int
    class Config:
        orm_mode = True

class TaskCreate(BaseModel):
    title: str
    description: Optional[str]
    column_id: int
    class Config:
        orm_mode = True

class TaskLogCreate(BaseModel):
    task_id: int
    action: str
    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class Project(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

class Column(BaseModel):
    id: int
    name: str
    project_id: int

    class Config:
        orm_mode = True

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str]
    column_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TaskLog(BaseModel):
    id: int
    task_id: int
    action: str
    timestamp: datetime

    class Config:
        orm_mode = True
