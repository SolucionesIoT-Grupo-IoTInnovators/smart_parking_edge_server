from datetime import datetime
from typing import Optional
from iam.domain.entities import EdgeServer, EdgeServerStatus
from iam.infrastructure.models import EdgeServer as EdgeServerModel


class EdgeServerRepository:
    
    @staticmethod
    def get_or_create_test_server(parking_id) -> Optional[EdgeServer]:
        """Get or create a test Edge Server for development purposes"""
        try:
            model, created = EdgeServerModel.get_or_create(
                edge_id="server-edge-001",
                defaults={
                    'parking_id': parking_id,
                    'name': "Test Edge Server",
                    'api_key': "test-api-key-123",
                    'ip_address': EdgeServerRepository.get_local_ip(),
                    'last_sync': datetime.now(),
                    'created_at': datetime.now()
                }
            )
            return EdgeServer(
                edge_id=model.edge_id,
                parking_id=model.parking_id,
                name=model.name,
                api_key=model.api_key,
                status=model.status,
                ip_address=model.ip_address,
                last_sync=model.last_sync.isoformat(),
                created_at=model.created_at.isoformat()
            )
        except Exception as e:
            print(f"Error getting or creating test edge server: {e}")
            return None
    
    @staticmethod
    def find_by_id_and_api_key(edge_id, api_key) -> Optional[EdgeServer]:
        """Search for an Edge Server by ID and API key"""
        try:
            model = EdgeServerModel.get(
                (EdgeServerModel.edge_id == edge_id) &
                (EdgeServerModel.api_key == api_key)
            )
            return EdgeServer(
                edge_id=model.edge_id,
                parking_id=model.parking_id,
                name=model.name,
                api_key=model.api_key,
                status=model.status,
                ip_address=model.ip_address,
                last_sync=model.last_sync.isoformat(),
                created_at=model.created_at.isoformat()
            )
        except EdgeServerModel.get().DoesNotExist:
            return None

    @staticmethod
    def update_last_sync(edge_id, timestamp=None):
        """Update the last sync timestamp for an Edge Server"""
        timestamp = timestamp or datetime.now()
        EdgeServerModel.update(last_sync=timestamp).where(
            EdgeServerModel.edge_id == edge_id
        ).execute()
        
    @staticmethod
    def get_local_ip():
        """Get the local IP address of the server"""
        import socket
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception as e:
            print(f"Error getting local IP address: {e}")
            mock_ip = "192.168.0.123"
            return mock_ip