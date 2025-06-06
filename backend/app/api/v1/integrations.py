"""
Third-party Integration API endpoints
"""

from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ...core.database_simple import get_db
from ...models import User
from ...api.dependencies_simple import get_current_active_user
from ...services.integrations.integration_manager import integration_manager

router = APIRouter()


class IntegrationConfig(BaseModel):
    """Integration configuration model"""
    integration_type: str = Field(..., description="Type of integration (erp, crm, procurement)")
    provider: str = Field(..., description="Provider name (sap, salesforce, ariba, etc.)")
    config: Dict[str, Any] = Field(..., description="Provider-specific configuration")
    name: str = Field(..., description="User-friendly name for the integration")
    description: str = Field(None, description="Optional description")


class IntegrationUpdate(BaseModel):
    """Integration update model"""
    name: str = Field(None, description="Updated name")
    description: str = Field(None, description="Updated description")
    config: Dict[str, Any] = Field(None, description="Updated configuration")


class SyncRequest(BaseModel):
    """Synchronization request model"""
    sync_type: str = Field("full", description="Type of sync (full, incremental)")


class RFPPublishRequest(BaseModel):
    """RFP publishing request model"""
    rfp_id: int = Field(..., description="RFP ID to publish")
    integration_id: str = Field(..., description="Integration to publish to")
    additional_config: Dict[str, Any] = Field(default_factory=dict, description="Additional publishing configuration")


@router.get("/providers")
async def get_available_providers(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, List[str]]:
    """Get list of available integration providers by type"""
    
    return await integration_manager.get_available_providers()


@router.post("/")
async def register_integration(
    integration_data: IntegrationConfig,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Register a new integration for the organization"""
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization"
        )
    
    # Check if user has permission to create integrations
    if not current_user.is_admin and current_user.role.value not in ['admin', 'super_admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create integrations"
        )
    
    try:
        result = await integration_manager.register_integration(
            organization_id=current_user.organization_id,
            integration_type=integration_data.integration_type,
            provider=integration_data.provider,
            config=integration_data.config,
            user_id=current_user.id
        )
        
        # Add user-provided metadata
        if result["success"]:
            integration_key = result["integration_id"]
            integration = integration_manager.integrations[integration_key]
            integration["name"] = integration_data.name
            integration["description"] = integration_data.description
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register integration: {str(e)}"
        )


@router.get("/")
async def list_integrations(
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, Any]]:
    """Get all integrations for the current user's organization"""
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization"
        )
    
    try:
        integrations = await integration_manager.get_integrations(current_user.organization_id)
        return integrations
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve integrations: {str(e)}"
        )


@router.get("/{integration_id}")
async def get_integration(
    integration_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get detailed information about a specific integration"""
    
    try:
        integration_status = await integration_manager.get_integration_status(integration_id)
        
        # Check if user has access to this integration
        if integration_id in integration_manager.integrations:
            integration = integration_manager.integrations[integration_id]
            if integration["organization_id"] != current_user.organization_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to access this integration"
                )
        
        return integration_status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve integration status: {str(e)}"
        )


@router.put("/{integration_id}")
async def update_integration(
    integration_id: str,
    update_data: IntegrationUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Update integration configuration"""
    
    if integration_id not in integration_manager.integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = integration_manager.integrations[integration_id]
    
    # Check permissions
    if integration["organization_id"] != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this integration"
        )
    
    if not current_user.is_admin and current_user.role.value not in ['admin', 'super_admin', 'manager']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update integrations"
        )
    
    try:
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            if field == "config" and value:
                # Validate new configuration if provided
                test_result = await integration_manager._test_connection(
                    integration["type"],
                    integration["provider"],
                    value
                )
                if not test_result["success"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Configuration test failed: {test_result['error']}"
                    )
                integration[field] = value
            elif value is not None:
                integration[field] = value
        
        integration["updated_by"] = current_user.id
        integration["updated_at"] = integration_manager.datetime.utcnow().isoformat()
        
        return {
            "success": True,
            "integration_id": integration_id,
            "message": "Integration updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update integration: {str(e)}"
        )


@router.delete("/{integration_id}")
async def remove_integration(
    integration_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Remove an integration"""
    
    if integration_id not in integration_manager.integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = integration_manager.integrations[integration_id]
    
    # Check permissions
    if integration["organization_id"] != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to remove this integration"
        )
    
    if not current_user.is_admin and current_user.role.value not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to remove integrations"
        )
    
    try:
        result = await integration_manager.remove_integration(integration_id, current_user.id)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove integration: {str(e)}"
        )


@router.post("/{integration_id}/sync")
async def sync_integration(
    integration_id: str,
    sync_request: SyncRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Trigger synchronization for an integration"""
    
    if integration_id not in integration_manager.integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = integration_manager.integrations[integration_id]
    
    # Check permissions
    if integration["organization_id"] != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to sync this integration"
        )
    
    try:
        # For demonstration, we'll run sync immediately
        # In production, this would typically be a background task
        result = await integration_manager.sync_integration(integration_id, sync_request.sync_type)
        
        return {
            "success": True,
            "integration_id": integration_id,
            "sync_started": True,
            "sync_result": result,
            "message": "Synchronization completed"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync integration: {str(e)}"
        )


@router.post("/{integration_id}/test")
async def test_integration_connection(
    integration_id: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Test connection for an integration"""
    
    if integration_id not in integration_manager.integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = integration_manager.integrations[integration_id]
    
    # Check permissions
    if integration["organization_id"] != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to test this integration"
        )
    
    try:
        test_result = await integration_manager._test_connection(
            integration["type"],
            integration["provider"],
            integration["config"]
        )
        
        return {
            "integration_id": integration_id,
            "test_result": test_result,
            "tested_at": integration_manager.datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test integration: {str(e)}"
        )


@router.post("/rfp/publish")
async def publish_rfp_to_platform(
    publish_request: RFPPublishRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Publish an RFP to a procurement platform"""
    
    from ...models.rfp_simple import RFP
    
    # Get RFP
    rfp = db.query(RFP).filter(RFP.id == publish_request.rfp_id).first()
    
    if not rfp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="RFP not found"
        )
    
    # Check permissions
    if not current_user.is_admin and rfp.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to publish this RFP"
        )
    
    # Get integration
    integration_id = publish_request.integration_id
    
    if integration_id not in integration_manager.integrations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found"
        )
    
    integration = integration_manager.integrations[integration_id]
    
    # Check if integration is for procurement
    if integration["type"] != "procurement":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Integration must be of type 'procurement' to publish RFPs"
        )
    
    try:
        # Prepare RFP data for publishing
        rfp_data = {
            "id": rfp.id,
            "title": rfp.title,
            "description": rfp.description,
            "rfp_number": rfp.rfp_number,
            "rfp_type": rfp.rfp_type.value if rfp.rfp_type else None,
            "estimated_budget": rfp.estimated_budget,
            "currency": rfp.currency,
            "submission_deadline": rfp.submission_deadline.isoformat() if rfp.submission_deadline else None,
            "requirements": rfp.requirements,
            "contact_person": rfp.contact_person,
            "contact_email": rfp.contact_email,
            **publish_request.additional_config
        }
        
        # Publish to platform
        result = await integration_manager.procurement_manager.publish_rfp(
            integration["provider"],
            integration["config"],
            rfp_data
        )
        
        return {
            "success": True,
            "rfp_id": publish_request.rfp_id,
            "integration_id": integration_id,
            "platform": integration["provider"],
            "publish_result": result,
            "message": f"RFP published to {integration['provider']} successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish RFP: {str(e)}"
        )


@router.get("/stats/summary")
async def get_integration_stats(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get integration statistics for the organization"""
    
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with an organization"
        )
    
    try:
        org_integrations = await integration_manager.get_integrations(current_user.organization_id)
        
        stats = {
            "total_integrations": len(org_integrations),
            "active_integrations": len([i for i in org_integrations if i.get("status") == "active"]),
            "by_type": {},
            "by_provider": {},
            "last_sync_times": [],
            "error_count": 0
        }
        
        for integration in org_integrations:
            # Count by type
            int_type = integration.get("type", "unknown")
            stats["by_type"][int_type] = stats["by_type"].get(int_type, 0) + 1
            
            # Count by provider
            provider = integration.get("provider", "unknown")
            stats["by_provider"][provider] = stats["by_provider"].get(provider, 0) + 1
            
            # Track sync times
            if integration.get("last_sync"):
                stats["last_sync_times"].append(integration["last_sync"])
            
            # Count errors
            stats["error_count"] += integration.get("error_count", 0)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve integration statistics: {str(e)}"
        )