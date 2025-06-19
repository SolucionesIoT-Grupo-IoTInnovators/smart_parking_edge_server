import json
import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from device.application.services import DeviceService
from shared.infrastructure.mqtt_client import mqtt_client

load_dotenv()
device_api = Blueprint('device_api', __name__)

device_service = DeviceService()
@device_api.route('/reservate', methods=['POST'])
def reservate_device():
    try:
        data = request.get_json()
        spot_id = data.get('spotId')
        reserved = data.get('reserved', False)

        if not spot_id:
            return jsonify({'error': 'Missing required fields'}), 400

        payload = {
            'spotId': spot_id,
            'apiKey': '',
            'reserved': reserved
        }

        updated_spot = device_service.update_device_status(spot_id, 'RESERVED' if reserved else 'AVAILABLE')
        mqtt_client.publish(os.getenv("MQTT_TOPIC_RESERVA"), json.dumps(payload), qos=1)
        return jsonify(updated_spot), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400