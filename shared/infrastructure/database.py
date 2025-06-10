"""
Database initialization module for the SmartParking Edge Server.
"""
from peewee import SqliteDatabase



# Initialize the database connection
db = SqliteDatabase('smart_parking.db')


def init_db() -> None:
    if db.is_closed():
        db.connect()
    from parking_spot.infrastructure.models import ParkingSpot
    from iam.infrastructure.models import Device
    db.create_tables([ParkingSpot, Device], safe=True)