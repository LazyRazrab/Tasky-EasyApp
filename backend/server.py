from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models for Ideas App
class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    color: str = "#6366f1"  # Default purple color
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CategoryCreate(BaseModel):
    name: str
    color: str = "#6366f1"

class Idea(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str  # Rich text content as HTML
    category_id: Optional[str] = None
    tags: List[str] = []
    is_archived: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class IdeaCreate(BaseModel):
    title: str
    content: str
    category_id: Optional[str] = None
    tags: List[str] = []

class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[str] = None
    tags: Optional[List[str]] = None
    is_archived: Optional[bool] = None

# Category endpoints
@api_router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    category_dict = category.dict()
    category_obj = Category(**category_dict)
    await db.categories.insert_one(category_obj.dict())
    return category_obj

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    categories = await db.categories.find({"$or": [{"deleted": {"$exists": False}}, {"deleted": False}]}).to_list(1000)
    return [Category(**cat) for cat in categories]

@api_router.delete("/categories/{category_id}")
async def delete_category(category_id: str):
    result = await db.categories.update_one(
        {"id": category_id}, 
        {"$set": {"deleted": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}

# Idea endpoints
@api_router.post("/ideas", response_model=Idea)
async def create_idea(idea: IdeaCreate):
    idea_dict = idea.dict()
    idea_obj = Idea(**idea_dict)
    await db.ideas.insert_one(idea_obj.dict())
    return idea_obj

@api_router.get("/ideas", response_model=List[Idea])
async def get_ideas(
    archived: Optional[bool] = None,
    category_id: Optional[str] = None,
    search: Optional[str] = None
):
    query = {"$or": [{"deleted": {"$exists": False}}, {"deleted": False}]}
    
    if archived is not None:
        query["is_archived"] = archived
    
    if category_id:
        query["category_id"] = category_id
        
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]
    
    ideas = await db.ideas.find(query).sort("created_at", -1).to_list(1000)
    return [Idea(**idea) for idea in ideas]

@api_router.get("/ideas/{idea_id}", response_model=Idea)
async def get_idea(idea_id: str):
    idea = await db.ideas.find_one({"id": idea_id, "$or": [{"deleted": {"$exists": False}}, {"deleted": False}]})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return Idea(**idea)

@api_router.put("/ideas/{idea_id}", response_model=Idea)
async def update_idea(idea_id: str, idea_update: IdeaUpdate):
    update_dict = {k: v for k, v in idea_update.dict().items() if v is not None}
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.ideas.update_one(
        {"id": idea_id}, 
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    updated_idea = await db.ideas.find_one({"id": idea_id})
    return Idea(**updated_idea)

@api_router.delete("/ideas/{idea_id}")
async def delete_idea(idea_id: str):
    result = await db.ideas.update_one(
        {"id": idea_id}, 
        {"$set": {"deleted": True}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Idea not found")
    return {"message": "Idea deleted"}

# Archive/unarchive idea
@api_router.patch("/ideas/{idea_id}/archive")
async def toggle_archive_idea(idea_id: str):
    idea = await db.ideas.find_one({"id": idea_id})
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    new_status = not idea.get("is_archived", False)
    await db.ideas.update_one(
        {"id": idea_id}, 
        {"$set": {"is_archived": new_status, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": f"Idea {'archived' if new_status else 'unarchived'}"}

# Stats endpoint
@api_router.get("/stats")
async def get_stats():
    total_ideas = await db.ideas.count_documents({"$or": [{"deleted": {"$exists": False}}, {"deleted": False}]})
    active_ideas = await db.ideas.count_documents({"is_archived": False, "$or": [{"deleted": {"$exists": False}}, {"deleted": False}]})
    archived_ideas = await db.ideas.count_documents({"is_archived": True, "$or": [{"deleted": {"$exists": False}}, {"deleted": False}]})
    total_categories = await db.categories.count_documents({"$or": [{"deleted": {"$exists": False}}, {"deleted": False}]})
    
    return {
        "total_ideas": total_ideas,
        "active_ideas": active_ideas,
        "archived_ideas": archived_ideas,
        "total_categories": total_categories
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()