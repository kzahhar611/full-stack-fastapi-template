"""
Version control system for collaborative document editing
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class VersionControlManager:
    """Manager for document version control"""
    
    def __init__(self):
        self.versions: Dict[int, List[Dict[str, Any]]] = {}
        self.current_versions: Dict[int, int] = {}
        
    def create_version(self, rfp_id: int, content: Dict[str, Any], user_id: int, message: str = None) -> Dict[str, Any]:
        """Create a new version of the document"""
        if rfp_id not in self.versions:
            self.versions[rfp_id] = []
            self.current_versions[rfp_id] = 0
        
        version_number = len(self.versions[rfp_id]) + 1
        version = {
            "version": version_number,
            "rfp_id": rfp_id,
            "content": content,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "message": message or f"Version {version_number}",
            "changes": self._calculate_changes(rfp_id, content)
        }
        
        self.versions[rfp_id].append(version)
        self.current_versions[rfp_id] = version_number
        return version
    
    def get_versions(self, rfp_id: int) -> List[Dict[str, Any]]:
        """Get all versions for an RFP"""
        return self.versions.get(rfp_id, [])
    
    def get_version(self, rfp_id: int, version_number: int) -> Optional[Dict[str, Any]]:
        """Get a specific version"""
        versions = self.versions.get(rfp_id, [])
        for version in versions:
            if version["version"] == version_number:
                return version
        return None
    
    def get_current_version(self, rfp_id: int) -> Optional[Dict[str, Any]]:
        """Get the current version"""
        if rfp_id not in self.current_versions:
            return None
        
        current_version_number = self.current_versions[rfp_id]
        return self.get_version(rfp_id, current_version_number)
    
    def revert_to_version(self, rfp_id: int, version_number: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Revert to a previous version"""
        version = self.get_version(rfp_id, version_number)
        if not version:
            return None
        
        # Create new version with reverted content
        return self.create_version(
            rfp_id,
            version["content"],
            user_id,
            f"Reverted to version {version_number}"
        )
    
    def _calculate_changes(self, rfp_id: int, new_content: Dict[str, Any]) -> List[str]:
        """Calculate changes from previous version"""
        changes = []
        
        if rfp_id not in self.versions or not self.versions[rfp_id]:
            changes.append("Initial version created")
            return changes
        
        # Get previous version
        previous_version = self.versions[rfp_id][-1]
        previous_content = previous_version["content"]
        
        # Simple change detection
        for key, value in new_content.items():
            if key not in previous_content:
                changes.append(f"Added {key}")
            elif previous_content[key] != value:
                changes.append(f"Modified {key}")
        
        for key in previous_content.keys():
            if key not in new_content:
                changes.append(f"Removed {key}")
        
        return changes if changes else ["Minor changes"]


# Global version control manager instance
version_control_manager = VersionControlManager()