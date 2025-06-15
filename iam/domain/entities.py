from enum import Enum
from datetime import datetime

class EdgeServerStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

class EdgeServer:
    def __init__(self, edge_id: str, parking_id: str, name: str = None,
                 api_key: str = None, status: str = None,
                 ip_address: str = None, last_sync: str = None, 
                 created_at: str = None):
        self.edge_id = edge_id
        self.parking_id = parking_id
        self.name = name or f"EdgeServer-{edge_id}"
        self.api_key = api_key
        self.status = status
        self.ip_address = ip_address
        self.last_sync = last_sync or datetime.now().isoformat()
        self.created_at = created_at or datetime.now().isoformat()