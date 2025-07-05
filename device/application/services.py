from iam.infrastructure.repositories import EdgeServerRepository
from parking_spot.infrastructure.repositories import ParkingSpotRepository


class DeviceService:
    def __init__(self):
        self.repository = ParkingSpotRepository()
        self.edgeRepository = EdgeServerRepository

    def provision_device(self, mac_address: str):
        spot = self.repository.get_by_mac(mac_address)
        edge = self.edgeRepository.get_edger_server()
        if spot:
            return {
                "mac": spot.mac_address.upper(),
                "status": spot.status,
                "apiKey": edge.api_key,
                "spotId": spot.spot_id,
                "label": spot.spot_label,
            }
        return None

    def update_device_status(self, spot_id: str, status: str):
        spot = self.repository.get_by_id(spot_id)
        if not spot:
            raise ValueError("Parking spot not found")

        updated_spot = self.repository.update_spot_status(spot_id, status)
        return {
            "mac": updated_spot.mac_address,
            "status": updated_spot.status,
            "spot": updated_spot.spot_id,
            "label": updated_spot.spot_label,
        }