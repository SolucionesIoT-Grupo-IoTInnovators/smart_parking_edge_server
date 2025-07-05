import os
import time
import threading

import paho.mqtt.client as mqtt
import json
import logging
from typing import Optional, Callable, Dict, Any
from dotenv import load_dotenv

from device.application.services import DeviceService
from iam.application.services import AuthApplicationService
from parking_spot.application.services import ParkingSpotApplicationService

load_dotenv()


class MQTTClient:
    def __init__(self, client_id: str, host: str = "localhost", port: int = 1883,
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        Args:
            client_id: Identificador único del cliente
            host: Dirección del broker MQTT
            port: Puerto del broker MQTT
            username: Usuario para autenticación (opcional)
            password: Contraseña para autenticación (opcional)
        """
        self.client_id = client_id
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)

        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        self.topic_callbacks: Dict[str, Callable] = {}

        self.pending_subscriptions: list = []

        self.is_connected = False
        self.connection_event = threading.Event()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            self.connection_event.set()  # Señalar que la conexión está lista
            self.logger.info(f"Conectado al broker MQTT en {self.host}:{self.port}")

            self._process_pending_subscriptions()
        else:
            self.is_connected = False
            self.connection_event.clear()
            self.logger.error(f"Error de conexión al broker MQTT. Código: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.is_connected = False
        self.connection_event.clear()
        if rc != 0:
            self.logger.warning(f"Desconexión inesperada del broker MQTT (código: {rc})")
        else:
            self.logger.info("Desconectado del broker MQTT")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode('utf-8')

        self.logger.info(f"Mensaje recibido en '{topic}': {payload}")

        if topic in self.topic_callbacks:
            try:
                self.topic_callbacks[topic](topic, payload)
            except Exception as e:
                self.logger.error(f"Error ejecutando callback para topic '{topic}': {e}")

        for registered_topic, callback in self.topic_callbacks.items():
            if self._topic_matches(registered_topic, topic):
                try:
                    callback(topic, payload)
                except Exception as e:
                    self.logger.error(f"Error ejecutando callback para pattern '{registered_topic}': {e}")

    def _topic_matches(self, pattern: str, topic: str) -> bool:
        if pattern == topic:
            return False

        pattern_parts = pattern.split('/')
        topic_parts = topic.split('/')

        if len(pattern_parts) != len(topic_parts):
            if '+' not in pattern and '#' not in pattern:
                return False

        for i, pattern_part in enumerate(pattern_parts):
            if pattern_part == '#':
                return True
            if i >= len(topic_parts):
                return False
            if pattern_part != '+' and pattern_part != topic_parts[i]:
                return False

        return True

    def _process_pending_subscriptions(self):
        for subscription in self.pending_subscriptions:
            topic, qos, callback = subscription
            self._do_subscribe(topic, qos, callback)
        self.pending_subscriptions.clear()

    def connect(self, timeout: int = 10) -> bool:
        """
        Args:
            timeout: Tiempo máximo de espera para la conexión
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            if self.username and self.password:
                self.client.username_pw_set(self.username, self.password)

            self.client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)

            self.client.reconnect_delay_set(min_delay=1, max_delay=120)

            self.client.connect(self.host, self.port, keepalive=60)

            self.client.loop_start()

            if self.connection_event.wait(timeout):
                return True
            else:
                self.logger.error(f"Timeout esperando conexión MQTT ({timeout}s)")
                return False

        except Exception as e:
            self.logger.error(f"Error conectando al broker MQTT: {e}")
            return False

    def wait_for_connection(self, timeout: int = 10) -> bool:
        """
        Args:
            timeout: Tiempo máximo de espera
        Returns:
            bool: True si está conectado
        """
        return self.connection_event.wait(timeout)

    def disconnect(self):
        if self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()

    def publish(self, topic: str, payload: Any, qos: int = 0, retain: bool = False) -> bool:
        """
        Args:
            topic: Topic donde publicar
            payload: Mensaje a publicar (puede ser string, dict, etc.)
            qos: Nivel de calidad de servicio (0, 1, 2)
            retain: Si el mensaje debe ser retenido por el broker
        Returns:
            bool: True si el mensaje fue publicado exitosamente
        """
        if not self.is_connected:
            self.logger.error("No hay conexión al broker MQTT")
            return False

        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            elif not isinstance(payload, str):
                payload = str(payload)

            result = self.client.publish(topic, payload, qos=qos, retain=retain)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Mensaje publicado en '{topic}': {payload}")
                return True
            else:
                self.logger.error(f"Error publicando mensaje en '{topic}'")
                return False

        except Exception as e:
            self.logger.error(f"Error publicando mensaje: {e}")
            return False

    def subscribe(self, topic: str, qos: int = 0, callback: Optional[Callable] = None) -> bool:
        """
        Args:
            topic: Topic al que suscribirse
            qos: Nivel de calidad de servicio
            callback: Función callback personalizada para este topic
        Returns:
            bool: True si la suscripción fue exitosa
        """
        if not self.is_connected:
            self.logger.info(f"Agregando suscripción pendiente para '{topic}'")
            self.pending_subscriptions.append((topic, qos, callback))
            return True

        return self._do_subscribe(topic, qos, callback)

    def _do_subscribe(self, topic: str, qos: int = 0, callback: Optional[Callable] = None) -> bool:
        try:
            result = self.client.subscribe(topic, qos=qos)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Suscrito al topic '{topic}'")

                if callback:
                    self.topic_callbacks[topic] = callback

                return True
            else:
                self.logger.error(f"Error suscribiéndose al topic '{topic}'")
                return False

        except Exception as e:
            self.logger.error(f"Error en suscripción: {e}")
            return False

    def unsubscribe(self, topic: str) -> bool:
        """
        Args:
            topic: Topic del que desuscribirse
        Returns:
            bool: True si se desuscribió exitosamente
        """
        if not self.is_connected:
            self.logger.error("No hay conexión al broker MQTT")
            return False

        try:
            result = self.client.unsubscribe(topic)

            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                self.logger.info(f"Desuscrito del topic '{topic}'")

                # Remover callback personalizado si existe
                if topic in self.topic_callbacks:
                    del self.topic_callbacks[topic]

                return True
            else:
                self.logger.error(f"Error desuscribiéndose del topic '{topic}'")
                return False

        except Exception as e:
            self.logger.error(f"Error en desuscripción: {e}")
            return False


mqtt_client_device = MQTTClient(
    client_id=f"flask_client_{int(time.time())}",
    host=os.getenv("MQTT_DEVICE_BROKER", "localhost"),
    port=int(os.getenv("MQTT_DEVICE_PORT")),
    username=os.getenv("MQTT_DEVICE_USERNAME"),
    password=os.getenv("MQTT_DEVICE_PASSWORD")
)

mqtt_client_cloud = MQTTClient(
    client_id=f"flask_client_cloud_{int(time.time())}",
    host=os.getenv("MQTT_CLOUD_BROKER", "localhost"),
    port=int(os.getenv("MQTT_CLOUD_PORT")),
    username=os.getenv("MQTT_CLOUD_USERNAME"),
    password=os.getenv("MQTT_CLOUD_PASSWORD")
)

device_service = DeviceService()
edge_service = AuthApplicationService()
parking_service = ParkingSpotApplicationService()

status_topic = os.getenv("MQTT_CLOUD_TOPIC_PARKING")
def on_device_status_update(topic: str, payload: str):
    try:
        data = json.loads(payload)
        spot_id = data.get("spotId")
        api_key = data.get("apiKey")
        occupied = data.get("occupied")
        if spot_id is not None and occupied is not None and api_key is not None:
            edge = edge_service.get_edge_server()
            status = "OCCUPIED" if occupied else "AVAILABLE"
            device_service.update_device_status(spot_id, status)

            mqtt_client_cloud.publish(status_topic + edge.edge_id, json.dumps({
                'spotId': spot_id,
                'apiKey': api_key,
                'occupied': occupied
            }), qos=1)

            print(f"Device status updated: spot_id={spot_id}, status={status}")
        else:
            print(f"Invalid data received: {data}")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Error processing device status update: {e}")


def on_device_provisioning_request(topic: str, payload: str):
    try:
        print("Received provisioning request on topic:", topic)
        data = json.loads(payload)
        mac = data.get("mac")
        if mac:
            mac = mac.lower()
            response = device_service.provision_device(mac)
            if response:
                print("Provisioning response:", response)
                mqtt_client_device.publish("provisioning/response", json.dumps(response), qos=1)
            else:
                print("No response from provisioning service")
        else:
            print("No MAC address in provisioning request")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in provisioning request: {e}")
    except Exception as e:
        print(f"Error processing provisioning request: {e}")


def on_cloud_provisioning_response(topic: str, payload: str):
    try:
        data = json.loads(payload)
        msg_type = data.get("type")
        if msg_type == "config":
            parking_id = data.get("parkingId")
            api_key = data.get("apiKey")
            server_id = data.get("serverId")
            edge_name = data.get("edgeName")

            if parking_id and api_key and server_id and edge_name:
                print(f"Received provisioning response for parkingId={parking_id}, serverId={server_id}")
                edge_service.get_or_create_test_edge_server(parking_id, edge_name, api_key, server_id)
                status_subscribe = mqtt_client_cloud.subscribe(status_topic + server_id, callback=on_cloud_status_update)
                print(f"Subscribed to cloud status updates for serverId={server_id}: {status_subscribe}")
            else:
                print("Invalid data in cloud provisioning response:", data)
        elif msg_type == "devices":
            devices = data.get("devices", [])
            if devices:
                print(f"Received {len(devices)} devices in cloud provisioning response")
                for device in devices:
                    print("Processing device:", device)
                    parking_service.create_parking_spot(device.get("macAddress"),device.get("deviceType"),
                                                device.get("status"), device.get("spotLabel"),
                                                device.get("spotId"), device.get("parkingId"), device.get("edgeId"))

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in cloud provisioning response: {e}")
    except Exception as e:
        print(f"Error processing cloud provisioning response: {e}")

def on_cloud_status_update(topic: str, payload: str):
    try:
        print("Received cloud status update on topic:", topic)
        data = json.loads(payload)
        if "reserved" in data:
            reserved = data["reserved"]
            spot_id = data["spotId"]
            api_key = data["apiKey"]

            payload = {
                'spotId': spot_id,
                'apiKey': api_key,
                'reserved': reserved
            }
            device_service.update_device_status(spot_id, 'RESERVED' if reserved else 'AVAILABLE')
            mqtt_client_device.publish(os.getenv("MQTT_DEVICE_TOPIC_RESERVA"), json.dumps(payload), qos=1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON in cloud status update: {e}")
    except Exception as e:
        print(f"Error processing cloud status update: {e}")