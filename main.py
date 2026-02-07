from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import httpx

import models, schemas, database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Travel Planner API")

ART_API_URL = "https://api.artic.edu/api/v1/artworks"
async def fetch_art_place(external_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ART_API_URL}/{external_id}")
        if resp.status_code == 404:
            return None
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Error connecting to Art API")
        data = resp.json()
        return data.get('data')

@app.post("/projects/", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
async def create_project(project: schemas.ProjectCreate, db: Session = Depends(database.get_db)):
    db_project = models.Project(
        name=project.name, 
        description=project.description, 
        start_date=project.start_date
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    if project.initial_places:
        if len(project.initial_places) > 10:
             raise HTTPException(status_code=400, detail="Cannot add more than 10 places to a project")
        
        for ext_id in project.initial_places:
            # Проверяем во внешнем API
            art_data = await fetch_art_place(ext_id)
            if not art_data:
                raise HTTPException(status_code=400, detail=f"Place with external ID {ext_id} not found in Art API")
            new_place = models.Place(
                project_id=db_project.id,
                external_id=ext_id,
                title=art_data.get('title', 'Unknown Art')
            )
            db.add(new_place)
        
        db.commit()
        db.refresh(db_project)
    
    return db_project

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(database.get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project_update: schemas.ProjectBase, db: Session = Depends(database.get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.name = project_update.name
    db_project.description = project_update.description
    db_project.start_date = project_update.start_date
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(database.get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    for place in db_project.places:
        if place.visited:
            raise HTTPException(status_code=400, detail="Cannot delete project with visited places")
    db.delete(db_project)
    db.commit()
    return {"detail": "Project deleted"}


@app.post("/projects/{project_id}/places/", response_model=schemas.Place)
async def add_place_to_project(project_id: int, place: schemas.PlaceCreate, db: Session = Depends(database.get_db)):
    # 1. search project
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 2. check limit (maks 10)
    if len(db_project.places) >= 10:
        raise HTTPException(status_code=400, detail="Project limit reached (max 10 places)")

    # 3. cheking dublicats in project
    for p in db_project.places:
        if p.external_id == place.external_id:
             raise HTTPException(status_code=400, detail="Place already exists in this project")

    # 4. check API
    art_data = await fetch_art_place(place.external_id)
    if not art_data:
        raise HTTPException(status_code=404, detail="Place not found in Art Institute API")

    # 5. save
    new_place = models.Place(
        project_id=project_id,
        external_id=place.external_id,
        title=art_data.get('title', 'Unknown Art'),
        notes=place.notes
    )
    db.add(new_place)
    db.commit()
    db.refresh(new_place)
    return new_place

@app.put("/places/{place_id}", response_model=schemas.Place)
def update_place(place_id: int, place_update: schemas.PlaceUpdate, db: Session = Depends(database.get_db)):
    db_place = db.query(models.Place).filter(models.Place.id == place_id).first()
    if not db_place:
        raise HTTPException(status_code=404, detail="Place not found")
    
    if place_update.notes is not None:
        db_place.notes = place_update.notes
    if place_update.visited is not None:
        db_place.visited = place_update.visited
    
    db.commit()
    db.refresh(db_place)
    return db_place

@app.get("/projects/{project_id}/places/", response_model=List[schemas.Place])
def read_project_places(project_id: int, db: Session = Depends(database.get_db)):
    if not db.query(models.Project).filter(models.Project.id == project_id).first():
        raise HTTPException(status_code=404, detail="Project not found")
        
    places = db.query(models.Place).filter(models.Place.project_id == project_id).all()
    return places