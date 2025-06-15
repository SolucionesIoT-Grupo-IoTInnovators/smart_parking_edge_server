import os, requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()


class BackendApiClient:
    """Client to communicate with the Smart Parking central backend"""

    def __init__(self):
        self.base_url = os.environ.get('CENTRAL_API_UR', 'http://localhost:8081/api/v1')
        self.api_key = os.environ.get('API_KEY', 'test-api-key-123')
        self.edge_server_id = os.environ.get('EDGE_SERVER_ID', 'test-edge-001')

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for HTTP requests"""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }

    def sign_in(self, username: str, password: str) -> bool:
        """Authenticate with the backend and get an access token"""
        try:
            payload = {
                'email': username,
                'password': password
            }

            response = requests.post(
                f"{self.base_url}/authentication/sign-in",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            self.api_key = data.get('token')
            os.environ['API_KEY'] = self.api_key

            dotenv_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')

            if os.path.exists(dotenv_file):
                with open(dotenv_file, 'r') as f:
                    lines = f.readlines()

                api_key_found = False
                for i, line in enumerate(lines):
                    if line.startswith('API_KEY='):
                        lines[i] = f'API_KEY={self.api_key}\n'
                        api_key_found = True
                        break

                if not api_key_found:
                    lines.append(f'API_KEY={self.api_key}\n')

                with open(dotenv_file, 'w') as f:
                    f.writelines(lines)
            else:
                with open(dotenv_file, 'w') as f:
                    f.write(f'API_KEY={self.api_key}\n')

            return True
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"Error during sign-in: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if the client has a valid API key"""
        return bool(self.api_key and self.api_key != 'test-api-key-123')

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the backend"""
        try:
            response = requests.get(
                f"{self.base_url}/{endpoint}",
                headers=self._get_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in GET request to {endpoint}: {e}")
            return {"error": str(e)}

    def post(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make a POST request to the backend"""
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self._get_headers(),
                json=data
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error in POST request to {endpoint}: {e}")
            return {"error": str(e)}