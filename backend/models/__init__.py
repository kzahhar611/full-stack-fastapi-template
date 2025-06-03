"""
TenderWise AI - Database Models
"""

from core.database import Base
from .user import User
from .rfp import RFP, RFPDocument
from .proposal import Proposal, ProposalDocument
from .project import Project

# TODO: Import additional models when implemented
# from .task import Task
# from .notification import Notification
# from .workflow import Workflow, WorkflowNode, WorkflowConnection
# from .ai_agent import AIAgent, AIModel
# from .document import Document, DocumentTemplate

__all__ = [
    "Base",
    "User",
    "RFP",
    "RFPDocument", 
    "Proposal",
    "ProposalDocument",
    "Project",
]