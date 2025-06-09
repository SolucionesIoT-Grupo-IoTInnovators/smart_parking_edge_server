"""
Database initialization module for the SmartParking Edge Server.
"""
from peewee import SqliteDatabase



# Initialize the database connection
db = SqliteDatabase('smart_parking.db')

def init_db() -> None:
    """
    Initialize the database connection. It also creates the necessary tables if they do not exist.
    """
    db.connect()
    """ 
    Create tables if they do not exist.
    """

    db.create_tables([], safe=True)  # Replace with actual model classes when defined