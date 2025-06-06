"""
Real-time synchronization manager for collaborative editing
"""

from typing import Dict, List, Optional, Any, Set
import asyncio
import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ...core.database_simple import get_db
from ...models import User


class ConnectionManager:
    """WebSocket connection manager for real-time collaboration"""
    
    def __init__(self):
        # Store active connections by room (RFP ID)
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Store user info for each connection
        self.connection_users: Dict[WebSocket, Dict[str, Any]] = {}
        # Store room participants
        self.room_participants: Dict[str, Set[int]] = {}
        
    async def connect(self, websocket: WebSocket, room_id: str, user: User):
        """Connect user to collaboration room"""
        await websocket.accept()
        
        # Add to room connections
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
            self.room_participants[room_id] = set()
        
        self.active_connections[room_id].append(websocket)
        self.connection_users[websocket] = {
            "user_id": user.id,
            "user_name": user.full_name or user.email,
            "room_id": room_id,
            "connected_at": datetime.utcnow().isoformat()
        }
        self.room_participants[room_id].add(user.id)
        
        # Notify room about new participant
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email,
                "email": user.email
            },
            "participants_count": len(self.room_participants[room_id]),
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_websocket=websocket)
        
        # Send current participants to new user
        participants = []
        for ws in self.active_connections[room_id]:
            if ws != websocket:
                user_info = self.connection_users.get(ws)
                if user_info:
                    participants.append({
                        "id": user_info["user_id"],
                        "name": user_info["user_name"]
                    })
        
        await websocket.send_text(json.dumps({
            "type": "room_state",
            "participants": participants,
            "participants_count": len(self.room_participants[room_id])
        }))
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect user from collaboration room"""
        user_info = self.connection_users.get(websocket)
        if not user_info:
            return
        
        room_id = user_info["room_id"]
        user_id = user_info["user_id"]
        
        # Remove from connections
        if room_id in self.active_connections:
            if websocket in self.active_connections[room_id]:
                self.active_connections[room_id].remove(websocket)
            
            # Remove from participants
            if user_id in self.room_participants.get(room_id, set()):
                self.room_participants[room_id].remove(user_id)
            
            # Clean up empty rooms
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                if room_id in self.room_participants:
                    del self.room_participants[room_id]
        
        # Remove connection info
        if websocket in self.connection_users:
            del self.connection_users[websocket]
        
        # Notify room about participant leaving
        asyncio.create_task(self.broadcast_to_room(room_id, {
            "type": "user_left",
            "user": {
                "id": user_id,
                "name": user_info["user_name"]
            },
            "participants_count": len(self.room_participants.get(room_id, set())),
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_websocket: Optional[WebSocket] = None):
        """Broadcast message to all users in a room"""
        if room_id not in self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected_sockets = []
        
        for websocket in self.active_connections[room_id]:
            if websocket == exclude_websocket:
                continue
            
            try:
                await websocket.send_text(message_text)
            except:
                # Connection is broken, mark for removal
                disconnected_sockets.append(websocket)
        
        # Clean up disconnected sockets
        for websocket in disconnected_sockets:
            self.disconnect(websocket)
    
    async def send_to_user(self, room_id: str, user_id: int, message: dict):
        """Send message to specific user in room"""
        if room_id not in self.active_connections:
            return
        
        message_text = json.dumps(message)
        
        for websocket in self.active_connections[room_id]:
            user_info = self.connection_users.get(websocket)
            if user_info and user_info["user_id"] == user_id:
                try:
                    await websocket.send_text(message_text)
                except:
                    self.disconnect(websocket)
                break
    
    def get_room_participants(self, room_id: str) -> List[Dict[str, Any]]:
        """Get list of participants in a room"""
        if room_id not in self.active_connections:
            return []
        
        participants = []
        for websocket in self.active_connections[room_id]:
            user_info = self.connection_users.get(websocket)
            if user_info:
                participants.append({
                    "id": user_info["user_id"],
                    "name": user_info["user_name"],
                    "connected_at": user_info["connected_at"]
                })
        
        return participants


class RealtimeManager:
    """Manager for real-time collaboration features"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        # Store document editing locks
        self.editing_locks: Dict[str, Dict[str, Any]] = {}
        # Store collaborative cursors
        self.cursors: Dict[str, Dict[int, Dict[str, Any]]] = {}
        
    async def handle_websocket(self, websocket: WebSocket, room_id: str, user: User):
        """Handle WebSocket connection for real-time collaboration"""
        await self.connection_manager.connect(websocket, room_id, user)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await self.process_message(websocket, room_id, user, message)
                
        except WebSocketDisconnect:
            self.connection_manager.disconnect(websocket)
            await self.release_user_locks(room_id, user.id)
        except Exception as e:
            print(f"WebSocket error: {e}")
            self.connection_manager.disconnect(websocket)
    
    async def process_message(self, websocket: WebSocket, room_id: str, user: User, message: dict):
        """Process incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "document_edit":
            await self.handle_document_edit(room_id, user, message)
        elif message_type == "cursor_update":
            await self.handle_cursor_update(room_id, user, message)
        elif message_type == "lock_section":
            await self.handle_lock_section(room_id, user, message)
        elif message_type == "unlock_section":
            await self.handle_unlock_section(room_id, user, message)
        elif message_type == "comment_add":
            await self.handle_comment_add(room_id, user, message)
        elif message_type == "typing_start":
            await self.handle_typing_status(room_id, user, message, True)
        elif message_type == "typing_stop":
            await self.handle_typing_status(room_id, user, message, False)
        else:
            # Echo unknown messages to room for extensibility
            await self.connection_manager.broadcast_to_room(room_id, {
                "type": "custom_message",
                "original_type": message_type,
                "user": {
                    "id": user.id,
                    "name": user.full_name or user.email
                },
                "data": message.get("data", {}),
                "timestamp": datetime.utcnow().isoformat()
            }, exclude_websocket=websocket)
    
    async def handle_document_edit(self, room_id: str, user: User, message: dict):
        """Handle document editing updates"""
        edit_data = message.get("data", {})
        
        # Broadcast edit to all participants except sender
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "document_edit",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email
            },
            "data": {
                "section": edit_data.get("section"),
                "content": edit_data.get("content"),
                "operation": edit_data.get("operation", "update"),
                "position": edit_data.get("position"),
                "length": edit_data.get("length")
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_cursor_update(self, room_id: str, user: User, message: dict):
        """Handle cursor position updates"""
        cursor_data = message.get("data", {})
        
        # Store cursor position
        if room_id not in self.cursors:
            self.cursors[room_id] = {}
        
        self.cursors[room_id][user.id] = {
            "position": cursor_data.get("position", 0),
            "selection": cursor_data.get("selection"),
            "section": cursor_data.get("section"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Broadcast cursor update
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "cursor_update",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email
            },
            "data": self.cursors[room_id][user.id],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_lock_section(self, room_id: str, user: User, message: dict):
        """Handle section locking for editing"""
        section_id = message.get("data", {}).get("section_id")
        
        if not section_id:
            return
        
        lock_key = f"{room_id}:{section_id}"
        
        # Check if section is already locked
        if lock_key in self.editing_locks:
            existing_lock = self.editing_locks[lock_key]
            if existing_lock["user_id"] != user.id:
                # Section is locked by another user
                await self.connection_manager.send_to_user(room_id, user.id, {
                    "type": "lock_denied",
                    "data": {
                        "section_id": section_id,
                        "locked_by": existing_lock["user_name"],
                        "locked_at": existing_lock["locked_at"]
                    }
                })
                return
        
        # Grant lock
        self.editing_locks[lock_key] = {
            "user_id": user.id,
            "user_name": user.full_name or user.email,
            "section_id": section_id,
            "locked_at": datetime.utcnow().isoformat()
        }
        
        # Broadcast lock to room
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "section_locked",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email
            },
            "data": {
                "section_id": section_id,
                "locked_at": self.editing_locks[lock_key]["locked_at"]
            }
        })
    
    async def handle_unlock_section(self, room_id: str, user: User, message: dict):
        """Handle section unlocking"""
        section_id = message.get("data", {}).get("section_id")
        
        if not section_id:
            return
        
        lock_key = f"{room_id}:{section_id}"
        
        # Check if user owns the lock
        if lock_key in self.editing_locks:
            lock = self.editing_locks[lock_key]
            if lock["user_id"] == user.id:
                # Release lock
                del self.editing_locks[lock_key]
                
                # Broadcast unlock to room
                await self.connection_manager.broadcast_to_room(room_id, {
                    "type": "section_unlocked",
                    "user": {
                        "id": user.id,
                        "name": user.full_name or user.email
                    },
                    "data": {
                        "section_id": section_id,
                        "unlocked_at": datetime.utcnow().isoformat()
                    }
                })
    
    async def handle_comment_add(self, room_id: str, user: User, message: dict):
        """Handle real-time comment addition"""
        comment_data = message.get("data", {})
        
        # Broadcast new comment to room
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "comment_added",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email
            },
            "data": {
                "comment_id": comment_data.get("comment_id"),
                "section": comment_data.get("section"),
                "content": comment_data.get("content"),
                "position": comment_data.get("position")
            },
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_typing_status(self, room_id: str, user: User, message: dict, is_typing: bool):
        """Handle typing status updates"""
        typing_data = message.get("data", {})
        
        # Broadcast typing status
        await self.connection_manager.broadcast_to_room(room_id, {
            "type": "typing_status",
            "user": {
                "id": user.id,
                "name": user.full_name or user.email
            },
            "data": {
                "is_typing": is_typing,
                "section": typing_data.get("section"),
                "position": typing_data.get("position")
            },
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_websocket=None)  # Don't exclude sender for typing status
    
    async def release_user_locks(self, room_id: str, user_id: int):
        """Release all locks held by a user"""
        locks_to_remove = []
        
        for lock_key, lock_data in self.editing_locks.items():
            if lock_data["user_id"] == user_id and lock_key.startswith(f"{room_id}:"):
                locks_to_remove.append(lock_key)
        
        for lock_key in locks_to_remove:
            lock_data = self.editing_locks[lock_key]
            del self.editing_locks[lock_key]
            
            # Broadcast unlock
            await self.connection_manager.broadcast_to_room(room_id, {
                "type": "section_unlocked",
                "user": {
                    "id": user_id,
                    "name": lock_data["user_name"]
                },
                "data": {
                    "section_id": lock_data["section_id"],
                    "unlocked_at": datetime.utcnow().isoformat(),
                    "reason": "user_disconnected"
                }
            })
    
    def get_room_status(self, room_id: str) -> Dict[str, Any]:
        """Get current status of a collaboration room"""
        participants = self.connection_manager.get_room_participants(room_id)
        
        # Get active locks for this room
        room_locks = []
        for lock_key, lock_data in self.editing_locks.items():
            if lock_key.startswith(f"{room_id}:"):
                room_locks.append(lock_data)
        
        # Get active cursors for this room
        room_cursors = self.cursors.get(room_id, {})
        
        return {
            "room_id": room_id,
            "participants": participants,
            "participants_count": len(participants),
            "active_locks": room_locks,
            "active_cursors": len(room_cursors),
            "status": "active" if participants else "inactive"
        }


# Global realtime manager instance
realtime_manager = RealtimeManager()