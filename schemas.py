from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class PlaceBase(BaseModel):
    notes: Optional[str] = None

class PlaceCreate(PlaceBase):
    external_id: int

class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None

class Place(PlaceBase):
    id: int
    project_id: int
    external_id: int
    title: str
    visited: bool

    class Config:
        from_attributes = True
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    initial_places: Optional[List[int]] = []

class Project(ProjectBase):
    id: int
    is_completed: bool
    places: List[Place] = []

    class Config:
        from_attributes = True