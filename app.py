from flask import Flask

import iam.application.services
from parking_spot.interfaces.services import parking_spot_api
from iam.interfaces.services import iam_api
from shared.infrastructure.database import init_db

app = Flask(__name__)

app.register_blueprint(iam_api)
app.register_blueprint(parking_spot_api)

first_request = True

@app.before_request
def setup():
    global first_request
    if first_request:
        init_db()
        first_request = False
        # Initialize the database and create a test device on the first request
        init_db()
        auth_application_service = iam.application.services.AuthApplicationService()
        auth_application_service.get_or_create_test_device()

    if __name__ == '__main__':
        app.run(debug=True)