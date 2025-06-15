from parking_spot.domain.services import ParkingSpotService
from parking_spot.infrastructure.repositories import ParkingSpotRepository
from iam.application.services import AuthApplicationService

class ParkingSpotApplicationService:
    def __init__(self):
        self.parking_spot_repository = ParkingSpotRepository()
        self.parking_spot_service = ParkingSpotService()
        self.iam_service = AuthApplicationService()
        
    def create_parking_spot(self, mac_address: str, device_type: str, spot_status: str, spot_label: str,
                            spot_id: str, parking_id: int, edge_id: int):

        # Create a new parking spot
        spot = self.parking_spot_service.create_spot(
            mac_address=mac_address,
            device_type=device_type,
            spot_status=spot_status,
            spot_label=spot_label,
            spot_id=spot_id,
            parking_id=parking_id,
            edge_id=edge_id
        )
        # Save the parking spot to the repository
        return self.parking_spot_repository.save(spot)

    def update_parking_spot(self, edge_id: str, spot_id: str, status: str, api_key: str):
        # Validate the device using the auth service
        if not self.iam_service.get_edge_server_by_id_and_api_key(edge_id, api_key):
            raise ValueError("Device not found or API key is invalid")

        # Retrieve the parking spot
        spot = self.parking_spot_repository.get_by_id(spot_id)
        if not spot:
            raise ValueError("Parking spot not found")

        # Update the parking spot status
        updated_spot = self.parking_spot_service.update_spot(spot, status)

        # Save the updated parking spot to the repository
        return self.parking_spot_repository.save(updated_spot)