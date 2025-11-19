"""
API dependencies
"""
from app.core.database import get_db

# Database dependency
async def get_database():
    """Get database session"""
    async for db in get_db():
        yield db
