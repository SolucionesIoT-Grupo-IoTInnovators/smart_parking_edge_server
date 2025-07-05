from typing import Dict

from flask import Blueprint, request, jsonify
import os, requests

from iam.application.services import AuthApplicationService

iam_api = Blueprint('iam', __name__)

auth_service = AuthApplicationService()


def authenticate_request():
    edge_id = request.json.get('edge_id') if request.json else None
    api_key = request.headers.get('X-API-Key')
    if not edge_id or not api_key:
        return jsonify({"error": "Missing edge_id or API key"}), 401
    if not auth_service.authenticate(edge_id, api_key):
        return jsonify({"error": "Invalid edge_id or API key"}), 401
    return None


def create_edge_server(parking_id, edge_name, api_key, edge_id):
    result = auth_service.get_or_create_test_edge_server(parking_id, edge_name, api_key, edge_id)
    if result:
        return result
    else:
        return jsonify({"error": "Failed to create edge server"}), 500

def _get_headers() -> Dict[str, str]:
    return {
        'Authorization': f'Bearer {os.environ.get("API_KEY")}',
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
    }
