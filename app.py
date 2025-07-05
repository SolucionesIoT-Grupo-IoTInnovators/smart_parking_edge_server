import json

from flask import Flask
from dotenv import load_dotenv
import os
from getmac import get_mac_address

from parking_spot.interfaces.services import parking_spot_api
from iam.interfaces.services import iam_api
from device.interfaces.services import device_api
from shared.infrastructure.backend_connector import BackendApiClient
from shared.infrastructure.database import init_db
from shared.infrastructure.mqtt_client import mqtt_client_device, mqtt_client_cloud, on_device_status_update, \
    on_device_provisioning_request, on_cloud_provisioning_response

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
app.register_blueprint(device_api)

mqtt_initialized = False


def initialize_mqtt():
    """Inicializa MQTT y las suscripciones"""
    global mqtt_initialized

    if mqtt_initialized:
        return

    print("Conectando a MQTT...")
    if mqtt_client_cloud.connect(timeout=15):
        print("✓ Conectado a MQTT broker para el backend")
        mac_address = get_mac_address()
        # Subscribe to the backend topics
        provisioning_topic = os.getenv("MQTT_CLOUD_TOPIC_PROVISIONING_RESPONSE")

        if provisioning_topic:
            provisioning_subscribe = mqtt_client_cloud.subscribe(f"{provisioning_topic}{mac_address}", callback=on_cloud_provisioning_response)
            print(f"✓ Suscrito a provisioning topic '{provisioning_topic}': {provisioning_subscribe}")

        provision_request = { "mac": mac_address.lower() }
        mqtt_client_cloud.publish(os.getenv("MQTT_CLOUD_TOPIC_PROVISIONING_REQUEST"), json.dumps(provision_request), qos=1)

    else:
        print("✗ Error conectando a MQTT broker para el backend")

    if mqtt_client_device.connect(timeout=15):
        print("✓ Conectado a MQTT broker")

        estado_topic = os.getenv("MQTT_DEVICE_TOPIC_ESTADO")
        provisioning_topic = os.getenv("MQTT_DEVICE_TOPIC_PROVISIONING_REQUEST")

        if estado_topic:
            estado_subscribe = mqtt_client_device.subscribe(estado_topic, callback=on_device_status_update)
            print(f"✓ Suscrito a reserva topic '{estado_topic}': {estado_subscribe}")

        if provisioning_topic:
            provisioning_subscribe = mqtt_client_device.subscribe(provisioning_topic, callback=on_device_provisioning_request)
            print(f"✓ Suscrito a provisioning topic '{provisioning_topic}': {provisioning_subscribe}")

        mqtt_initialized = True
    else:
        print("✗ Error conectando a MQTT broker")

@app.before_request
def setup():
    init_db()


if __name__ == '__main__':
    initialize_mqtt()

    try:
        app.run(debug=True, use_reloader=False)
    finally:
        print("Desconectando MQTT...")
        mqtt_client_device.disconnect()
        mqtt_client_cloud.disconnect()