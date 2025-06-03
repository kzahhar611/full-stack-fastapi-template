"""
TenderWise AI - Proposal Service
"""

import secrets
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException, status

from models.proposal import Proposal, ProposalStatus, ProposalDocument
from models.rfp import RFP
from models.user import User
from schemas.proposal import ProposalCreate, ProposalUpdate, ProposalFilters


class ProposalService:
    """Business logic for proposal operations"""
    
    @staticmethod
    def generate_proposal_number() -> str:
        """Generate unique proposal number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_part = secrets.token_hex(3).upper()
        return f"PROP-{timestamp}-{random_part}"
    
    @staticmethod
    def get_proposals(
        db: Session,
        filters: ProposalFilters = None,
        current_user: User = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Proposal]:
        """Get proposals with filtering and pagination"""
        query = db.query(Proposal).options(
            joinedload(Proposal.documents)
        )
        
        # Apply user access control
        if not current_user.is_superuser:
            # Regular users can only see their own proposals or submitted ones
            query = query.filter(
                or_(
                    Proposal.created_by == current_user.id,
                    Proposal.status == ProposalStatus.SUBMITTED
                )
            )
        
        if filters:
            # Search filter
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Proposal.title.ilike(search_term),
                        Proposal.proposal_number.ilike(search_term),
                        Proposal.executive_summary.ilike(search_term)
                    )
                )
            
            # Status filter
            if filters.status:
                query = query.filter(Proposal.status == filters.status)
            
            # RFP filter
            if filters.rfp_id:
                query = query.filter(Proposal.rfp_id == filters.rfp_id)
            
            # My proposals filter
            if filters.my_proposals:
                query = query.filter(Proposal.created_by == current_user.id)
            
            # Cost range filters
            if filters.min_cost is not None:
                query = query.filter(Proposal.total_cost >= filters.min_cost)
            if filters.max_cost is not None:
                query = query.filter(Proposal.total_cost <= filters.max_cost)
            
            # Ordering
            order_column = getattr(Proposal, filters.order_by, Proposal.created_at)
            if filters.order_direction == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        else:
            query = query.order_by(desc(Proposal.created_at))
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_proposal_by_id(db: Session, proposal_id: int) -> Optional[Proposal]:
        """Get proposal by ID with related data"""
        return db.query(Proposal).options(
            joinedload(Proposal.documents)
        ).filter(Proposal.id == proposal_id).first()
    
    @staticmethod
    def create_proposal(
        db: Session, 
        proposal_data: ProposalCreate, 
        current_user: User
    ) -> Proposal:
        """Create new proposal"""
        # Validate RFP exists and user can create proposals for it
        rfp = db.query(RFP).filter(RFP.id == proposal_data.rfp_id).first()
        if not rfp:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RFP not found"
            )
        
        # Check if RFP is still accepting proposals
        if rfp.status not in ["published", "under_review"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="RFP is not accepting proposals"
            )
        
        # Generate unique proposal number
        proposal_number = ProposalService.generate_proposal_number()
        
        # Create proposal
        proposal = Proposal(
            **proposal_data.model_dump(exclude={"rfp_id"}),
            rfp_id=proposal_data.rfp_id,
            proposal_number=proposal_number,
            created_by=current_user.id,
            status=ProposalStatus.DRAFT
        )
        
        db.add(proposal)
        db.commit()
        db.refresh(proposal)
        
        return proposal
    
    @staticmethod
    def update_proposal(
        db: Session, 
        proposal_id: int, 
        proposal_data: ProposalUpdate,
        current_user: User
    ) -> Optional[Proposal]:
        """Update proposal"""
        proposal = ProposalService.get_proposal_by_id(db, proposal_id)
        if not proposal:
            return None
        
        # Check permissions
        if not ProposalService.can_user_edit_proposal(proposal, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to edit this proposal"
            )
        
        # Check if proposal can be edited
        if proposal.status == ProposalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot edit submitted proposal"
            )
        
        # Update fields
        update_data = proposal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(proposal, field, value)
        
        proposal.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(proposal)
        
        return proposal
    
    @staticmethod
    def update_proposal_status(
        db: Session, 
        proposal_id: int, 
        status: ProposalStatus,
        current_user: User
    ) -> Optional[Proposal]:
        """Update proposal status"""
        proposal = ProposalService.get_proposal_by_id(db, proposal_id)
        if not proposal:
            return None
        
        # Check permissions for status changes
        if not ProposalService.can_user_change_status(proposal, status, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to change proposal status"
            )
        
        # Validate status transition
        if not ProposalService.is_valid_status_transition(proposal.status, status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status transition from {proposal.status} to {status}"
            )
        
        proposal.status = status
        proposal.updated_at = datetime.utcnow()
        
        # Set submitted_at when submitting
        if status == ProposalStatus.SUBMITTED and not proposal.submitted_at:
            proposal.submitted_at = datetime.utcnow()
        
        db.commit()
        db.refresh(proposal)
        
        return proposal
    
    @staticmethod
    def delete_proposal(db: Session, proposal_id: int, current_user: User) -> bool:
        """Delete proposal"""
        proposal = ProposalService.get_proposal_by_id(db, proposal_id)
        if not proposal:
            return False
        
        # Check permissions
        if not ProposalService.can_user_edit_proposal(proposal, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this proposal"
            )
        
        # Check if proposal can be deleted
        if proposal.status == ProposalStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete submitted proposal"
            )
        
        db.delete(proposal)
        db.commit()
        
        return True
    
    @staticmethod
    def can_user_edit_proposal(proposal: Proposal, user: User) -> bool:
        """Check if user can edit proposal"""
        return user.is_superuser or proposal.created_by == user.id
    
    @staticmethod
    def can_user_change_status(proposal: Proposal, new_status: ProposalStatus, user: User) -> bool:
        """Check if user can change proposal status"""
        # Superusers can change any status
        if user.is_superuser:
            return True
        
        # Proposal creators can submit their own proposals
        if proposal.created_by == user.id and new_status == ProposalStatus.SUBMITTED:
            return True
        
        # Proposal creators can withdraw their own proposals
        if proposal.created_by == user.id and new_status == ProposalStatus.WITHDRAWN:
            return True
        
        return False
    
    @staticmethod
    def is_valid_status_transition(current_status: ProposalStatus, new_status: ProposalStatus) -> bool:
        """Validate proposal status transitions"""
        valid_transitions = {
            ProposalStatus.DRAFT: [
                ProposalStatus.IN_PROGRESS,
                ProposalStatus.SUBMITTED,
                ProposalStatus.WITHDRAWN
            ],
            ProposalStatus.IN_PROGRESS: [
                ProposalStatus.DRAFT,
                ProposalStatus.SUBMITTED,
                ProposalStatus.WITHDRAWN
            ],
            ProposalStatus.SUBMITTED: [
                ProposalStatus.UNDER_REVIEW,
                ProposalStatus.WITHDRAWN
            ],
            ProposalStatus.UNDER_REVIEW: [
                ProposalStatus.ACCEPTED,
                ProposalStatus.REJECTED
            ],
            ProposalStatus.ACCEPTED: [],  # Final state
            ProposalStatus.REJECTED: [],  # Final state
            ProposalStatus.WITHDRAWN: []  # Final state
        }
        
        return new_status in valid_transitions.get(current_status, [])