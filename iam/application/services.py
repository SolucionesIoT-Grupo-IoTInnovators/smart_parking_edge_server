from typing import Optional

from iam.domain.entities import EdgeServer
from iam.domain.services import AuthService
from iam.infrastructure.repositories import EdgeServerRepository


class AuthApplicationService:
    def __init__(self):
        self.edge_server_repository = EdgeServerRepository()
        self.auth_service = AuthService()

    def authenticate(self, edge_id: str, api_key: str) -> bool:
        edge_server: Optional[EdgeServer] = self.edge_server_repository.find_by_id_and_api_key(edge_id, api_key)
        return self.auth_service.authenticate(edge_server)

    def get_or_create_test_edge_server(self, parking_id: int, edge_name: str, api_key:str, edge_id:str) -> EdgeServer:
        return self.edge_server_repository.get_or_create_test_server(parking_id, edge_name, api_key, edge_id)

    def get_edge_server(self) -> Optional[EdgeServer]:
        return self.edge_server_repository.get_edger_server()

    def get_edge_server_by_id_and_api_key(self, edge_id: str, api_key: str) -> Optional[EdgeServer]:
        return self.edge_server_repository.find_by_id_and_api_key(edge_id, api_key)