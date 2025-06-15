class ParkingSpot:
    def __init__(self, mac_address=None, device_type=None, spot_id=None, status=None,
                 spot_label=None, parking_id=None, edge_id=None, last_updated=None, created_at=None):
        self.mac_address = mac_address
        self.device_type = device_type
        self.spot_id = spot_id
        self.status = status
        self.spot_label = spot_label
        self.parking_id = parking_id
        self.edge_id = edge_id
        self.last_updated = last_updated
        self.created_at = created_at