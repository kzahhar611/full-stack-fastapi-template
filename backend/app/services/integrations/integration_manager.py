"""
Central Integration Manager for third-party systems
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import asyncio
from sqlalchemy.orm import Session
from fastapi import HTTPException

from ...core.database_simple import get_db
from ...models import Organization, User
from .erp_connectors import ERPConnectorFactory
from .crm_sync import CRMSyncManager
from .procurement_apis import ProcurementAPIManager

class IntegrationManager:
    """Central manager for all third-party integrations"""
    
    def __init__(self):
        self.erp_factory = ERPConnectorFactory()
        self.crm_manager = CRMSyncManager()
        self.procurement_manager = ProcurementAPIManager()
        
        # Integration registry
        self.integrations: Dict[str, Dict] = {}
        
    async def register_integration(self, 
                                 organization_id: int,
                                 integration_type: str,
                                 provider: str,
                                 config: Dict[str, Any],
                                 user_id: int) -> Dict[str, Any]:
        """Register a new integration for an organization"""
        
        integration_key = f"{organization_id}_{integration_type}_{provider}"
        
        # Validate configuration based on provider
        if not self._validate_config(integration_type, provider, config):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid configuration for {provider} {integration_type} integration"
            )
        
        # Test connection
        connection_test = await self._test_connection(integration_type, provider, config)
        if not connection_test["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"Connection test failed: {connection_test['error']}"
            )
        
        # Store integration configuration
        integration_data = {
            "organization_id": organization_id,
            "type": integration_type,
            "provider": provider,
            "config": config,
            "status": "active",
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_sync": None,
            "sync_count": 0,
            "error_count": 0
        }
        
        self.integrations[integration_key] = integration_data
        
        return {
            "success": True,
            "integration_id": integration_key,
            "message": f"{provider} {integration_type} integration registered successfully",
            "connection_test": connection_test
        }
    
    async def sync_integration(self, integration_id: str, sync_type: str = "full") -> Dict[str, Any]:
        """Perform synchronization for a specific integration"""
        
        if integration_id not in self.integrations:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = self.integrations[integration_id]
        
        try:
            sync_result = None
            
            if integration["type"] == "erp":
                connector = self.erp_factory.get_connector(
                    integration["provider"],
                    integration["config"]
                )
                sync_result = await connector.sync_data(sync_type)
                
            elif integration["type"] == "crm":
                sync_result = await self.crm_manager.sync_provider(
                    integration["provider"],
                    integration["config"],
                    sync_type
                )
                
            elif integration["type"] == "procurement":
                sync_result = await self.procurement_manager.sync_platform(
                    integration["provider"],
                    integration["config"],
                    sync_type
                )
            
            # Update integration statistics
            integration["last_sync"] = datetime.utcnow().isoformat()
            integration["sync_count"] += 1
            
            if not sync_result["success"]:
                integration["error_count"] += 1
            
            return {
                "success": True,
                "integration_id": integration_id,
                "sync_result": sync_result,
                "message": f"Synchronization completed for {integration['provider']}"
            }
            
        except Exception as e:
            integration["error_count"] += 1
            integration["last_error"] = str(e)
            integration["last_error_at"] = datetime.utcnow().isoformat()
            
            return {
                "success": False,
                "integration_id": integration_id,
                "error": str(e),
                "message": f"Synchronization failed for {integration['provider']}"
            }
    
    async def get_integrations(self, organization_id: int) -> List[Dict[str, Any]]:
        """Get all integrations for an organization"""
        
        org_integrations = []
        
        for integration_id, integration in self.integrations.items():
            if integration["organization_id"] == organization_id:
                # Remove sensitive config data for display
                display_integration = integration.copy()
                display_integration["config"] = self._sanitize_config(integration["config"])
                display_integration["integration_id"] = integration_id
                org_integrations.append(display_integration)
        
        return org_integrations
    
    async def remove_integration(self, integration_id: str, user_id: int) -> Dict[str, Any]:
        """Remove an integration"""
        
        if integration_id not in self.integrations:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = self.integrations[integration_id]
        
        # Perform cleanup if needed
        try:
            if integration["type"] == "erp":
                connector = self.erp_factory.get_connector(
                    integration["provider"],
                    integration["config"]
                )
                await connector.cleanup()
                
            elif integration["type"] == "crm":
                await self.crm_manager.cleanup_provider(
                    integration["provider"],
                    integration["config"]
                )
                
            elif integration["type"] == "procurement":
                await self.procurement_manager.cleanup_platform(
                    integration["provider"],
                    integration["config"]
                )
        except Exception as e:
            # Log cleanup error but continue with removal
            pass
        
        # Remove from registry
        del self.integrations[integration_id]
        
        return {
            "success": True,
            "message": f"Integration {integration_id} removed successfully"
        }
    
    async def get_available_providers(self) -> Dict[str, List[str]]:
        """Get list of available integration providers by type"""
        
        return {
            "erp": ["sap", "oracle", "microsoft_dynamics", "netsuite", "generic"],
            "crm": ["salesforce", "hubspot", "microsoft_dynamics", "zoho", "generic"],
            "procurement": ["ariba", "coupa", "jaggaer", "ivalua", "generic"]
        }
    
    async def get_integration_status(self, integration_id: str) -> Dict[str, Any]:
        """Get detailed status of an integration"""
        
        if integration_id not in self.integrations:
            raise HTTPException(status_code=404, detail="Integration not found")
        
        integration = self.integrations[integration_id]
        
        # Get real-time status
        status_check = await self._test_connection(
            integration["type"],
            integration["provider"],
            integration["config"]
        )
        
        return {
            "integration_id": integration_id,
            "provider": integration["provider"],
            "type": integration["type"],
            "status": integration["status"],
            "connection_status": status_check["success"],
            "last_sync": integration.get("last_sync"),
            "sync_count": integration.get("sync_count", 0),
            "error_count": integration.get("error_count", 0),
            "last_error": integration.get("last_error"),
            "created_at": integration["created_at"]
        }
    
    def _validate_config(self, integration_type: str, provider: str, config: Dict[str, Any]) -> bool:
        """Validate integration configuration"""
        
        required_fields = {
            "erp": {
                "sap": ["host", "username", "password", "client"],
                "oracle": ["host", "username", "password", "service_name"],
                "microsoft_dynamics": ["tenant_id", "client_id", "client_secret"],
                "netsuite": ["account_id", "consumer_key", "consumer_secret", "token_id", "token_secret"],
                "generic": ["api_url", "api_key"]
            },
            "crm": {
                "salesforce": ["client_id", "client_secret", "username", "password", "security_token"],
                "hubspot": ["api_key"],
                "microsoft_dynamics": ["tenant_id", "client_id", "client_secret"],
                "zoho": ["client_id", "client_secret", "refresh_token"],
                "generic": ["api_url", "api_key"]
            },
            "procurement": {
                "ariba": ["api_key", "realm", "client_id", "client_secret"],
                "coupa": ["api_key", "instance_url"],
                "jaggaer": ["username", "password", "server_url"],
                "ivalua": ["api_key", "tenant_id"],
                "generic": ["api_url", "api_key"]
            }
        }
        
        if integration_type not in required_fields:
            return False
        
        if provider not in required_fields[integration_type]:
            return False
        
        required = required_fields[integration_type][provider]
        
        for field in required:
            if field not in config or not config[field]:
                return False
        
        return True
    
    async def _test_connection(self, integration_type: str, provider: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Test connection to integration provider"""
        
        try:
            if integration_type == "erp":
                connector = self.erp_factory.get_connector(provider, config)
                return await connector.test_connection()
                
            elif integration_type == "crm":
                return await self.crm_manager.test_connection(provider, config)
                
            elif integration_type == "procurement":
                return await self.procurement_manager.test_connection(provider, config)
            
            return {"success": False, "error": "Unknown integration type"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config for display"""
        
        sensitive_fields = [
            "password", "api_key", "client_secret", "security_token",
            "refresh_token", "token_secret", "private_key"
        ]
        
        sanitized = config.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                if sanitized[field]:
                    sanitized[field] = "*" * 8
        
        return sanitized


# Global integration manager instance
integration_manager = IntegrationManager()