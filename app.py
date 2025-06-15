from flask import Flask
from dotenv import load_dotenv
import os
from flasgger import Swagger

import iam.application.services
import parking_spot.interfaces.services
from parking_spot.interfaces.services import parking_spot_api
from iam.interfaces.services import iam_api
from shared.infrastructure.backend_connector import BackendApiClient
from shared.infrastructure.database import init_db

load_dotenv()

backend_client = BackendApiClient()
username = os.environ.get('PARKING_OWNER_USERNAME')
password = os.environ.get('PARKING_OWNER_PASSWORD')

if username and password and not backend_client.is_authenticated():
    if backend_client.sign_in(username, password):
        print("Successfully authenticated with backend")
    else:
        print("Failed to authenticate with backend")

app = Flask(__name__)

app.register_blueprint(iam_api)
app.register_blueprint(parking_spot_api)

first_request = True

@app.before_request
def setup():
    global first_request
    if first_request:
        first_request = False
        # Initialize the database and create a test device on the first request
        init_db()
        parking_id = int(os.environ.get('PARKING_ID', 1))
        edge = iam.interfaces.services.create_edge_server(parking_id)
        print("Edge server created:", edge.edge_id)
        spots = parking_spot.interfaces.services.create_parking_spot(parking_id, edge.edge_id)
        print("Parking spots created:", spots)

if __name__ == '__main__':
    app.run(debug=True)