"""
Common Pydantic schemas used across the application
"""
from typing import Any, Dict, List, Optional, Generic, TypeVar, Union
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from uuid import UUID

T = TypeVar('T')


class StatusResponse(BaseModel):
    """Standard status response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=100)
    pages: int
    
    @classmethod
    def create(cls, items: List[T], total: int, page: int, size: int):
        """Create paginated response"""
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: datetime


class UUIDMixin(BaseModel):
    """Mixin for UUID fields"""
    uuid: str
    
    @field_serializer('uuid')
    def serialize_uuid(self, uuid_val: Union[UUID, str]) -> str:
        """Convert UUID to string"""
        return str(uuid_val)


class UserReference(BaseModel):
    """Reference to a user"""
    id: int
    email: str
    full_name: str
    avatar_url: Optional[str] = None


class OrganizationReference(BaseModel):
    """Reference to an organization"""
    id: int
    uuid: str
    name: str
    slug: str
    logo_url: Optional[str] = None


# Common query parameters
class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.size


class SortParams(BaseModel):
    """Sorting query parameters"""
    sort_by: str = "created_at"
    sort_order: str = Field("desc", pattern="^(asc|desc)$")


class SearchParams(BaseModel):
    """Search query parameters"""
    search: Optional[str] = Field(None, min_length=1, max_length=100)
    

class FilterParams(BaseModel):
    """Common filter parameters"""
    status: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


# Error schemas
class ErrorDetail(BaseModel):
    """Error detail"""
    type: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    errors: Optional[List[ErrorDetail]] = None
    
    
# Health check response
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime
    version: str
    database: str
    uptime: int  # seconds