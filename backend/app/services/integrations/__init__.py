"""
Integration services for third-party platforms
"""

from .integration_manager import IntegrationManager
from .erp_connectors import ERPConnectorFactory
from .crm_sync import CRMSyncManager
from .procurement_apis import ProcurementAPIManager

__all__ = [
    "IntegrationManager",
    "ERPConnectorFactory", 
    "CRMSyncManager",
    "ProcurementAPIManager"
]