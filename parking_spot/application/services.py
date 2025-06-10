from parking_spot.domain.services import ParkingSpotService
from parking_spot.infrastructure.repositories import ParkingSpotRepository
from iam.application.services import AuthApplicationService

class ParkingSpotApplicationService:
    def __init__(self):
        self.parking_spot_repository = ParkingSpotRepository()
        self.parking_spot_service = ParkingSpotService()
        self.iam_service = AuthApplicationService()
        
    def create_parking_spot(self, device_id: str, mac_address: str, state: str, created_at: str, api_key: str):
        # Validate the device using the auth service
        if not self.iam_service.get_device_by_id_and_api_key(device_id, api_key):
            raise ValueError("Device not found or API key is invalid")

        # Create a new parking spot
        spot = self.parking_spot_service.create_spot(device_id, mac_address, state, created_at)
        # Save the parking spot to the repository
        return self.parking_spot_repository.save(spot)