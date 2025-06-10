from typing import Optional

from iam.infrastructure.models import Device as DeviceModel
from iam.domain.entities import Device

class DeviceRepository:
    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        try:
            device = DeviceModel.get((DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key))
            return Device(device.device_id, device.api_key, device.created_at)
        except DeviceModel.get().DoesNotExist:
            return None


    @staticmethod
    def get_or_create_test_device() -> Optional[Device]:
        from datetime import datetime
        device, created = DeviceModel.get_or_create(
            device_id = "smart-band-001",
            defaults = {
                'api_key': 'test-api-key-123',
                'created_at': datetime.now()
            }
        )
        return Device(device.device_id, device.api_key, created)