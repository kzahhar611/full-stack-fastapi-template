"""
TenderWise AI - RFP Service
"""

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from models.rfp import RFP, RFPStatus, RFPDocument
from models.user import User
from schemas.rfp import RFPCreate, RFPUpdate

class RFPService:
    """RFP business logic service"""

    @staticmethod
    def generate_rfp_number() -> str:
        """Generate unique RFP number"""
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_id = str(uuid.uuid4().hex[:6]).upper()
        return f"RFP-{timestamp}-{unique_id}"

    @staticmethod
    def create_rfp(
        db: Session, 
        rfp_data: RFPCreate, 
        created_by: int
    ) -> RFP:
        """Create new RFP"""
        # Generate unique RFP number
        rfp_number = RFPService.generate_rfp_number()
        
        # Ensure uniqueness
        while db.query(RFP).filter(RFP.rfp_number == rfp_number).first():
            rfp_number = RFPService.generate_rfp_number()
        
        # Create RFP
        rfp = RFP(
            **rfp_data.dict(),
            rfp_number=rfp_number,
            status=RFPStatus.DRAFT,
            created_by=created_by,
            issue_date=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(rfp)
        db.commit()
        db.refresh(rfp)
        
        return rfp

    @staticmethod
    def get_rfp_by_id(db: Session, rfp_id: int) -> Optional[RFP]:
        """Get RFP by ID"""
        return db.query(RFP).filter(RFP.id == rfp_id).first()

    @staticmethod
    def get_rfp_by_number(db: Session, rfp_number: str) -> Optional[RFP]:
        """Get RFP by number"""
        return db.query(RFP).filter(RFP.rfp_number == rfp_number).first()

    @staticmethod
    def get_rfps(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[RFPStatus] = None,
        created_by: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> List[RFP]:
        """Get RFPs with filtering and pagination"""
        query = db.query(RFP)
        
        # Apply filters
        if status:
            query = query.filter(RFP.status == status)
        
        if created_by:
            query = query.filter(RFP.created_by == created_by)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (RFP.title.ilike(search_term)) |
                (RFP.description.ilike(search_term)) |
                (RFP.rfp_number.ilike(search_term)) |
                (RFP.organization.ilike(search_term))
            )
        
        # Apply ordering
        if hasattr(RFP, order_by):
            order_column = getattr(RFP, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_rfp(
        db: Session,
        rfp_id: int,
        rfp_update: RFPUpdate,
        updated_by: int
    ) -> Optional[RFP]:
        """Update RFP"""
        rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
        if not rfp:
            return None
        
        # Update fields
        update_data = rfp_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rfp, field, value)
        
        rfp.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rfp)
        
        return rfp

    @staticmethod
    def update_rfp_status(
        db: Session,
        rfp_id: int,
        new_status: RFPStatus,
        updated_by: int
    ) -> Optional[RFP]:
        """Update RFP status"""
        rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
        if not rfp:
            return None
        
        # Update status with business logic
        if new_status == RFPStatus.PUBLISHED and rfp.status == RFPStatus.DRAFT:
            rfp.issue_date = datetime.utcnow()
        elif new_status == RFPStatus.AWARDED:
            rfp.award_date = datetime.utcnow()
        
        rfp.status = new_status
        rfp.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(rfp)
        
        return rfp

    @staticmethod
    def delete_rfp(db: Session, rfp_id: int) -> bool:
        """Delete RFP (soft delete by changing status)"""
        rfp = db.query(RFP).filter(RFP.id == rfp_id).first()
        if not rfp:
            return False
        
        # Only allow deletion of draft RFPs
        if rfp.status != RFPStatus.DRAFT:
            return False
        
        # Soft delete by changing status
        rfp.status = RFPStatus.CANCELLED
        rfp.updated_at = datetime.utcnow()
        
        db.commit()
        
        return True

    @staticmethod
    def get_rfp_documents(db: Session, rfp_id: int) -> List[RFPDocument]:
        """Get documents for an RFP"""
        return db.query(RFPDocument).filter(RFPDocument.rfp_id == rfp_id).all()

    @staticmethod
    def can_user_edit_rfp(rfp: RFP, user: User) -> bool:
        """Check if user can edit RFP"""
        # Superusers can edit any RFP
        if user.is_superuser:
            return True
        
        # Creator can edit their own RFPs if status allows
        if rfp.created_by == user.id and rfp.status in [RFPStatus.DRAFT, RFPStatus.UNDER_REVIEW]:
            return True
        
        return False

    @staticmethod
    def can_user_view_rfp(rfp: RFP, user: User) -> bool:
        """Check if user can view RFP"""
        # Superusers can view any RFP
        if user.is_superuser:
            return True
        
        # Creator can view their own RFPs
        if rfp.created_by == user.id:
            return True
        
        # Published RFPs are visible to all users
        if rfp.status == RFPStatus.PUBLISHED:
            return True
        
        return False