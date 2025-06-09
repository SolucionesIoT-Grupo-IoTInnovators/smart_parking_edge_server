from datetime import timezone, datetime

from dateutil.parser import parse

from parking_spot.domain.entities import ParkingSpot


class ParkingSpotService:
    def __init__(self):
        pass

    @staticmethod
    def create_spot(device_id: str, mac_address: str, status: str, created_at: str | None) -> ParkingSpot:
        try:
            if not (status == "AVAILABLE" or status == "OCCUPIED" or status == "RESERVED"):
                raise ValueError("Invalid status")
            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid status or created_at format")

        return ParkingSpot(device_id, status, parsed_created_at)
