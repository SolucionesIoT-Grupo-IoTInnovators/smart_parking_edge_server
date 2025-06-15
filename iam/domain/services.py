from typing import Optional

from iam.domain.entities import EdgeServer


class AuthService:
    def __init__(self):
        pass

    @staticmethod
    def authenticate(edge_server: Optional[EdgeServer]) -> bool:
        return edge_server is not None