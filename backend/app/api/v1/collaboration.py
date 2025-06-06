"""
Collaboration API endpoints for real-time features
"""

from typing import Any, List, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ...core.database_simple import get_db
from ...models import User
from ...api.dependencies_simple import get_current_active_user
from ...services.collaboration.realtime_sync import realtime_manager

router = APIRouter()


class CommentCreate(BaseModel):
    """Comment creation model"""
    rfp_id: int = Field(..., description="RFP ID")
    section: str = Field(..., description="Section of the RFP")
    content: str = Field(..., description="Comment content")
    position: int = Field(0, description="Position in the section")
    parent_comment_id: int = Field(None, description="Parent comment for replies")


class CommentResponse(BaseModel):
    """Comment response model"""
    id: int
    rfp_id: int
    section: str
    content: str
    position: int
    parent_comment_id: int = None
    author: Dict[str, Any]
    created_at: str
    updated_at: str = None
    replies: List['CommentResponse'] = []


class CollaborationStatus(BaseModel):
    """Collaboration status model"""
    rfp_id: int
    participants: List[Dict[str, Any]]
    active_locks: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


@router.websocket("/ws/{rfp_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    rfp_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time collaboration"""
    
    try:
        # Authenticate user via token
        # In a real implementation, you'd decode and validate the JWT token
        # For now, we'll use a simplified approach
        
        # Get user from token (simplified - in production, decode JWT properly)
        from ...api.dependencies_simple import get_user_from_token
        user = await get_user_from_token(token, db)
        
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Check if user has access to this RFP
        from ...models.rfp_simple import RFP
        rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
        
        if not rfp:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Check permissions
        if not user.is_admin and rfp.organization_id != user.organization_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        # Handle WebSocket connection
        await realtime_manager.handle_websocket(websocket, str(rfp_id), user)
        
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)


@router.get("/{rfp_id}/status")
async def get_collaboration_status(
    rfp_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get collaboration status for an RFP"""
    
    from ...models.rfp_simple import RFP
    
    # Check if RFP exists and user has access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this RFP"
        )
    
    # Get collaboration status
    room_status = realtime_manager.get_room_status(str(rfp_id))
    
    return {
        "rfp_id": rfp_id,
        "collaboration_status": room_status,
        "websocket_url": f"/api/v1/collaboration/ws/{rfp_id}",
        "features": {
            "real_time_editing": True,
            "collaborative_comments": True,
            "section_locking": True,
            "typing_indicators": True,
            "cursor_tracking": True
        }
    }


@router.post("/{rfp_id}/comments")
async def create_comment(
    rfp_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new comment on an RFP"""
    
    from ...models.rfp_simple import RFP
    
    # Verify RFP access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to comment on this RFP"
        )
    
    # For demonstration, we'll store comments in memory
    # In production, you'd store these in a database
    comment_id = len(getattr(realtime_manager, 'comments', [])) + 1
    
    comment = {
        "id": comment_id,
        "rfp_id": rfp_id,
        "section": comment_data.section,
        "content": comment_data.content,
        "position": comment_data.position,
        "parent_comment_id": comment_data.parent_comment_id,
        "author": {
            "id": current_user.id,
            "name": current_user.full_name or current_user.email,
            "email": current_user.email
        },
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": None,
        "replies": []
    }
    
    # Store comment (in production, save to database)
    if not hasattr(realtime_manager, 'comments'):
        realtime_manager.comments = []
    realtime_manager.comments.append(comment)
    
    # Broadcast comment to collaboration room
    await realtime_manager.connection_manager.broadcast_to_room(str(rfp_id), {
        "type": "comment_added",
        "user": {
            "id": current_user.id,
            "name": current_user.full_name or current_user.email
        },
        "data": {
            "comment_id": comment_id,
            "section": comment_data.section,
            "content": comment_data.content,
            "position": comment_data.position,
            "author": comment["author"]
        },
        "timestamp": comment["created_at"]
    })
    
    return {
        "success": True,
        "comment": comment,
        "message": "Comment created successfully"
    }


@router.get("/{rfp_id}/comments")
async def get_comments(
    rfp_id: int,
    section: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get comments for an RFP"""
    
    from ...models.rfp_simple import RFP
    
    # Verify RFP access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view comments on this RFP"
        )
    
    # Get comments from memory (in production, query database)
    all_comments = getattr(realtime_manager, 'comments', [])
    
    # Filter comments for this RFP
    rfp_comments = [c for c in all_comments if c["rfp_id"] == rfp_id]
    
    # Filter by section if specified
    if section:
        rfp_comments = [c for c in rfp_comments if c["section"] == section]
    
    # Organize comments by parent-child relationships
    root_comments = []
    comments_by_id = {c["id"]: c for c in rfp_comments}
    
    for comment in rfp_comments:
        if comment["parent_comment_id"] is None:
            # Root comment
            comment["replies"] = []
            root_comments.append(comment)
        else:
            # Reply comment
            parent = comments_by_id.get(comment["parent_comment_id"])
            if parent:
                parent["replies"].append(comment)
    
    return root_comments


@router.get("/{rfp_id}/activity")
async def get_collaboration_activity(
    rfp_id: int,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get recent collaboration activity for an RFP"""
    
    from ...models.rfp_simple import RFP
    
    # Verify RFP access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view activity on this RFP"
        )
    
    # Generate mock activity data
    # In production, this would come from an activity log
    import random
    from datetime import datetime, timedelta
    
    activities = []
    activity_types = [
        "document_edit", "comment_added", "section_locked", 
        "section_unlocked", "user_joined", "user_left"
    ]
    
    for i in range(min(limit, 20)):
        activity = {
            "id": i + 1,
            "type": random.choice(activity_types),
            "user": {
                "id": random.randint(1, 5),
                "name": f"User {random.randint(1, 5)}"
            },
            "details": {
                "section": f"section_{random.randint(1, 5)}",
                "description": f"Activity {i + 1} description"
            },
            "timestamp": (datetime.utcnow() - timedelta(minutes=i * 5)).isoformat()
        }
        activities.append(activity)
    
    return activities


@router.post("/{rfp_id}/lock/{section_id}")
async def lock_section(
    rfp_id: int,
    section_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Lock a section for editing"""
    
    from ...models.rfp_simple import RFP
    
    # Verify RFP access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this RFP"
        )
    
    lock_key = f"{rfp_id}:{section_id}"
    
    # Check if section is already locked
    if lock_key in realtime_manager.editing_locks:
        existing_lock = realtime_manager.editing_locks[lock_key]
        if existing_lock["user_id"] != current_user.id:
            return {
                "success": False,
                "error": "Section is already locked by another user",
                "locked_by": existing_lock["user_name"],
                "locked_at": existing_lock["locked_at"]
            }
    
    # Grant lock
    realtime_manager.editing_locks[lock_key] = {
        "user_id": current_user.id,
        "user_name": current_user.full_name or current_user.email,
        "section_id": section_id,
        "locked_at": datetime.utcnow().isoformat()
    }
    
    # Broadcast lock to room
    await realtime_manager.connection_manager.broadcast_to_room(str(rfp_id), {
        "type": "section_locked",
        "user": {
            "id": current_user.id,
            "name": current_user.full_name or current_user.email
        },
        "data": {
            "section_id": section_id,
            "locked_at": realtime_manager.editing_locks[lock_key]["locked_at"]
        }
    })
    
    return {
        "success": True,
        "message": f"Section {section_id} locked successfully",
        "lock_info": realtime_manager.editing_locks[lock_key]
    }


@router.delete("/{rfp_id}/lock/{section_id}")
async def unlock_section(
    rfp_id: int,
    section_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Unlock a section"""
    
    from ...models.rfp_simple import RFP
    
    # Verify RFP access
    rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this RFP"
        )
    
    lock_key = f"{rfp_id}:{section_id}"
    
    # Check if user owns the lock
    if lock_key in realtime_manager.editing_locks:
        lock = realtime_manager.editing_locks[lock_key]
        if lock["user_id"] == current_user.id or current_user.is_admin:
            # Release lock
            del realtime_manager.editing_locks[lock_key]
            
            # Broadcast unlock to room
            await realtime_manager.connection_manager.broadcast_to_room(str(rfp_id), {
                "type": "section_unlocked",
                "user": {
                    "id": current_user.id,
                    "name": current_user.full_name or current_user.email
                },
                "data": {
                    "section_id": section_id,
                    "unlocked_at": datetime.utcnow().isoformat()
                }
            })
            
            return {
                "success": True,
                "message": f"Section {section_id} unlocked successfully"
            }
        else:
            return {
                "success": False,
                "error": "You don't own this lock",
                "locked_by": lock["user_name"]
            }
    else:
        return {
            "success": False,
            "error": "Section is not locked"
        }