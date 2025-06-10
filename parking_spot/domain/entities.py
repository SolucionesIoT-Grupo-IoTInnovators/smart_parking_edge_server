class ParkingSpot:
    def __init__(self, device_id, mac_address, state, created_at, id=None):
        self.id = id
        self.device_id = device_id
        self.mac_address = mac_address
        self.state = state
        self.created_at = created_at