from peewee import Model, AutoField, CharField, IntegerField
from shared.infrastructure.database import db

class ParkingSpot(Model):
    spot_id = CharField(primary_key=True)
    spot_label = CharField()
    status = CharField()
    mac_address = CharField(null=True)
    parking_id = IntegerField()
    edge_id = CharField()
    device_type = CharField()
    last_updated = CharField()
    created_at = CharField()

    class Meta:
        database = db
        table_name = 'parking_spots'  # Ensure the table name is pluralized