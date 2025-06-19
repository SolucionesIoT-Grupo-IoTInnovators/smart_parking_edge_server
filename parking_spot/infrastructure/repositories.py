from parking_spot.infrastructure.models import ParkingSpot as ParkingSpotModel
from parking_spot.domain.entities import ParkingSpot
from datetime import datetime

class ParkingSpotRepository:
    @staticmethod
    def save(parking_spot):
        spot = ParkingSpotModel.create(
            spot_id = parking_spot.spot_id,
            spot_label = parking_spot.spot_label,
            status = parking_spot.status,
            mac_address = parking_spot.mac_address,
            parking_id = parking_spot.parking_id,
            edge_id = parking_spot.edge_id,
            device_type = parking_spot.device_type,
            last_updated = datetime.now(),
            created_at = datetime.now()
        )
        return ParkingSpot(
            spot_id=spot.spot_id,
            spot_label=spot.spot_label,
            status=spot.status,
            mac_address=spot.mac_address,
            parking_id=spot.parking_id,
            edge_id=spot.edge_id,
            device_type=spot.device_type,
            last_updated=spot.last_updated,
            created_at=spot.created_at
        )

    @staticmethod
    def update_spot_status(spot_id, status):
        spot = ParkingSpotModel.get(spot_id=spot_id)
        if not spot:
            raise ValueError("Parking spot not found")
        
        spot.status = status
        spot.last_updated = datetime.now()
        spot.save()
        return ParkingSpot(
            spot_id=spot.spot_id,
            spot_label=spot.spot_label,
            status=spot.status,
            mac_address=spot.mac_address,
            parking_id=spot.parking_id,
            edge_id=spot.edge_id,
            device_type=spot.device_type,
            last_updated=spot.last_updated,
            created_at=spot.created_at
        )

    @staticmethod
    def get_by_id(spot_id):
        spot = ParkingSpotModel.get(spot_id=spot_id)
        if not spot:
            return None
        return ParkingSpot(
            spot_id=spot.spot_id,
            spot_label=spot.spot_label,
            status=spot.status,
            mac_address=spot.mac_address,
            parking_id=spot.parking_id,
            edge_id=spot.edge_id,
            device_type=spot.device_type,
            last_updated=spot.last_updated,
            created_at=spot.created_at
        )

    @staticmethod
    def get_by_mac(mac_address):
        mac_address = mac_address.lower()
        spot = ParkingSpotModel.get(mac_address=mac_address)
        return ParkingSpot(
            spot_id=spot.spot_id,
            spot_label=spot.spot_label,
            status=spot.status,
            mac_address=spot.mac_address,
            parking_id=spot.parking_id,
            edge_id=spot.edge_id,
            device_type=spot.device_type,
            last_updated=spot.last_updated,
            created_at=spot.created_at
        )