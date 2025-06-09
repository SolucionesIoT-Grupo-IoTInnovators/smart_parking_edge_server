from peewee import Model, AutoField, CharField
from shared.infrastructure.database import db

class ParkingSpot(Model):
    id = AutoField()
    device_id = CharField()
    mac_address = CharField()
    state = CharField()
    created_at = CharField()

    class Meta:
        database = db
        table_name = 'parking_spots'  # Ensure the table name is pluralized