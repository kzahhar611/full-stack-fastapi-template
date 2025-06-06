"""
Comment system for collaborative RFP editing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class CommentManager:
    """Manager for comment system in collaborative editing"""
    
    def __init__(self):
        self.comments: Dict[int, List[Dict[str, Any]]] = {}
        
    def add_comment(self, rfp_id: int, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new comment to an RFP"""
        if rfp_id not in self.comments:
            self.comments[rfp_id] = []
        
        comment_id = len(self.comments[rfp_id]) + 1
        comment = {
            "id": comment_id,
            "rfp_id": rfp_id,
            "content": comment_data.get("content"),
            "section": comment_data.get("section"),
            "position": comment_data.get("position", 0),
            "author": comment_data.get("author"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": None,
            "parent_comment_id": comment_data.get("parent_comment_id"),
            "replies": []
        }
        
        self.comments[rfp_id].append(comment)
        return comment
    
    def get_comments(self, rfp_id: int) -> List[Dict[str, Any]]:
        """Get all comments for an RFP"""
        return self.comments.get(rfp_id, [])
    
    def update_comment(self, rfp_id: int, comment_id: int, content: str) -> Optional[Dict[str, Any]]:
        """Update a comment"""
        if rfp_id not in self.comments:
            return None
        
        for comment in self.comments[rfp_id]:
            if comment["id"] == comment_id:
                comment["content"] = content
                comment["updated_at"] = datetime.utcnow().isoformat()
                return comment
        
        return None
    
    def delete_comment(self, rfp_id: int, comment_id: int) -> bool:
        """Delete a comment"""
        if rfp_id not in self.comments:
            return False
        
        self.comments[rfp_id] = [
            comment for comment in self.comments[rfp_id] 
            if comment["id"] != comment_id
        ]
        return True


# Global comment manager instance
comment_manager = CommentManager()