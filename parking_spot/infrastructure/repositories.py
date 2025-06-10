from parking_spot.infrastructure.models import ParkingSpot as ParkingSpotModel
from parking_spot.domain.entities import ParkingSpot

class ParkingSpotRepository:
    def save(self, parking_spot):
        spot = ParkingSpotModel.create(
            device_id = parking_spot.device_id,
            mac_address = parking_spot.mac_address,
            state = parking_spot.state,
            created_at = parking_spot.created_at
        )
        return ParkingSpot(
            parking_spot.device_id,
            parking_spot.mac_address,
            parking_spot.state,
            parking_spot.created_at,
            spot.id
        )