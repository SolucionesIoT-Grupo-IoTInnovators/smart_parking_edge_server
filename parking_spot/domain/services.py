from datetime import timezone, datetime

from dateutil.parser import parse

from parking_spot.domain.entities import ParkingSpot


class ParkingSpotService:
    def __init__(self):
        pass

    @staticmethod
    def create_spot(mac_address: str, device_type: str, spot_status: str, spot_label: str, spot_id: str,
                    parking_id: int, edge_id: int) -> ParkingSpot:
        return ParkingSpot(
            mac_address=mac_address,
            device_type=device_type,
            spot_id=spot_id,
            status=spot_status,
            spot_label=spot_label,
            parking_id=parking_id,
            edge_id=edge_id,
            last_updated=datetime.now(timezone.utc).isoformat(),
            created_at=datetime.now(timezone.utc).isoformat()
        )


    @staticmethod
    def update_spot(spot: ParkingSpot, status: str) -> ParkingSpot:
        if status not in ["AVAILABLE", "OCCUPIED", "RESERVED"]:
            raise ValueError("Invalid status")
        
        spot.status = status
        spot.last_updated = datetime.now(timezone.utc).isoformat()

        return spot