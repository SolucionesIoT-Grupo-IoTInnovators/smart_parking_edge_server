from peewee import *
from shared.infrastructure.database import db
from datetime import datetime

class EdgeServer(Model):
    edge_id = CharField(primary_key=True)
    parking_id = IntegerField()
    name = CharField(null=True)
    api_key = CharField(null=True)
    status = CharField(default="ONLINE")
    mac_address = CharField(null=True)
    last_sync = DateTimeField(default=datetime.now)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        database = db
        table_name = 'edge_servers'