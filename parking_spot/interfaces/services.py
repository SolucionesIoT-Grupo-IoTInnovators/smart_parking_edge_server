from flask import Blueprint, request, jsonify

from parking_spot.application.services import ParkingSpotApplicationService
from iam.interfaces.services import authenticate_request

parking_spot_api = Blueprint('parking_spot_api', __name__)

parking_spot_service = ParkingSpotApplicationService()

@parking_spot_api.route('/api/v1/parking_spots', methods=['POST'])
def create_parking_spot():
    auth_result = authenticate_request()
    if auth_result:
        return auth_result
    data = request.json
    try:
        device_id = data['device_id']
        mac_address = data['mac_address']
        state = data['state']
        created_at = data.get('created_at')
        spot = parking_spot_service.create_parking_spot(device_id, mac_address, state, created_at,
                                                        request.headers.get('X-API-Key'))

        return jsonify({
            'id': spot.id,
            'device_id': spot.device_id,
            'mac_address': spot.mac_address,
            'state': spot.state,
            'created_at': spot.created_at.isoformat() + 'Z'
        }), 201
    except KeyError:
        return jsonify({'error': 'Missing required fields'}), 400
    except ValueError as e:
        return jsonify({'error': str(e)}), 400