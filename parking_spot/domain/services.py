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
            if not device_id or not mac_address:
                raise ValueError("Device ID and MAC address cannot be empty")
            parsed_mac_address = mac_address.lower()
            if not parsed_mac_address.replace(":", "").isalnum():
                raise ValueError("Invalid MAC address format")
            if len(parsed_mac_address) != 17:
                raise ValueError("MAC address must be 17 characters long")
            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid status or created_at format")

        return ParkingSpot(device_id, parsed_mac_address, status, parsed_created_at)
