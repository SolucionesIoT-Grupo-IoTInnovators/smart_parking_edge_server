from typing import Dict

from flask import Blueprint, jsonify
import os, requests

from parking_spot.application.services import ParkingSpotApplicationService

parking_spot_api = Blueprint('parking_spot_api', __name__)

parking_spot_service = ParkingSpotApplicationService()

def create_parking_spot(parking_id, edge_id):
    try:
        base_url = os.environ.get('CENTRAL_API_URL', 'http://localhost:8081/api/v1')
        response = requests.get(
            f"{base_url}/devices/unassigned/{parking_id}",
            headers=_get_headers()
        )
        if response.status_code == 200:
            devices = response.json()

            print(f"{len(devices)} unassigned devices were found.")
            for i, device in enumerate(devices):
                print(f"Device {i + 1}:", device)
                spot = parking_spot_service.create_parking_spot(
                    mac_address=device['macAddress'],
                    device_type='DISTANCE_SENSOR',
                    spot_status=device['spotStatus'],
                    spot_label=device['spotLabel'],
                    spot_id=device['parkingSpotId'],
                    parking_id=parking_id,
                    edge_id=edge_id
                )
                update_device(spot.spot_id, edge_id, spot.device_type)

            return jsonify(devices), 200
        else:
            print(f"Failed to fetch unassigned devices: {response.text}")
            return jsonify({"error": "Failed to fetch unassigned devices"}), 500
    except KeyError:
        return jsonify({'error': 'Missing required fields'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def update_device(spot_id: str, edge_id: str, device_type: str):
    try:
        base_url = os.environ.get('CENTRAL_API_UR', 'http://localhost:8081/api/v1')
        response = requests.put(
            f"{base_url}/devices/{spot_id}",
            json={
                'edgeId': edge_id,
                'macAddress': ' ',
                'type': device_type
            },
            headers=_get_headers()
        )
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            print(f"Failed to update device: {response.text}")
            return jsonify({"error": "Failed to update device"}), 500
    except KeyError:
        return jsonify({'error': 'Missing required fields'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def _get_headers() -> Dict[str, str]:
    return {
        'Authorization': f'Bearer {os.environ.get("API_KEY")}',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }