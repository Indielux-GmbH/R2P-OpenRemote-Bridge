import paho.mqtt.client as mqtt_client
from logging import getLogger
from logger.main import Logger as Logger
import configparser
import ssl
import time
from queue import Queue

class MqttConnector:

    def __init__(self, mqtt_id, mqtt_password='', config_file='config.ini'):
        self.connected = False

        # Read the config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        # Fill variables with data from config file
        self.mqtt_hostname = self.config['mqtt']['host']
        self.mqtt_host_port = int(self.config['mqtt']['port'])
        try:
            self.ca_certs=self.config['mqtt']['ca_certs']
            self.certfile=self.config['mqtt']['certfile']
            self.keyfile=self.config['mqtt']['keyfile']
        except KeyError:
            try:
                getLogger(__name__).warn('MQTT TLS Config not complete - try setting only ca_certs')
                self.ca_certs=self.config['mqtt']['ca_certs']
            except KeyError:
                getLogger(__name__).error('MQTT config: ca_certs is not defined in config!')
        self.mqtt_id = mqtt_id
        self.mqtt_password = mqtt_password

        # Start MQTT client
        self.client = mqtt_client.Client(self.mqtt_id)
        try:
            getLogger(__name__).debug('Set MQTT tls options')
            self.client.tls_set(ca_certs=self.ca_certs, certfile=self.certfile, keyfile=self.keyfile)
        except AttributeError:
            getLogger(__name__).debug("No Full TLS config - just ca_certs or certfile or keyfile defined!")
            try:
                getLogger(__name__).debug('Try setting ca_certs only')
                self.client.tls_set(ca_certs=self.ca_certs, cert_reqs=ssl.CERT_NONE)
            except AttributeError:
                getLogger(__name__).error('Cant set tls options giving up with defaults from config')
        getLogger(__name__).debug(f'Set MQTT username: {self.mqtt_id} and password: {self.mqtt_password}')
        self.client.username_pw_set(username=self.mqtt_id, password=self.mqtt_password)
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        
        self.client.connect_async(host=self.mqtt_hostname, port=self.mqtt_host_port)
        self.client.loop_start()

        self.message_received = False
        self.q = Queue()

    def on_connect(self, client, userdata, flags, rc):
        msg_ids = ["Connection accepted",
                   "Connection refused unacceptable protocol version",
                   "Connection refused, identifier rejected",
                   "Connection refused, server unavailable",
                   "Connection refused, bad user name or password",
                   "Connection refused, not authorized"]
        if rc == 0:
            getLogger(__name__).info(f"Client {self.mqtt_id} connected to Broker {self.mqtt_hostname} with msg id {rc} - {msg_ids[rc]}")
            getLogger(__name__).debug(f"Client: {client} | Userdata: {userdata} | Flags: {flags}")
            self.connected = True
            return True
        else:
            getLogger(__name__).critical(f"Failed to connect Broker with msg id {rc} - {msg_ids[rc]}")
            self.connected = False
            return False

    def on_disconnect(self, client, userdata, rc):
        getLogger(__name__).debug("MQTT Client disconnected.")
        self.connected = False

    def on_message(self, client, userdata, message):
        getLogger(__name__).debug(f"message payload: {str(message.payload.decode('utf-8'))}")
        getLogger(__name__).debug(f"message topic: {message.topic}")
        self.message_received = True
        self.q.put(f'{{"topic": "{message.topic}", "message": {str(message.payload.decode("utf-8"))}}}')

    def sub_topics(self, topics):
        """
        :param topics: an array with tubles of topci like this [(self.mqtt_topics[0], 2), (self.mqtt_topics[1], 1), (self.mqtt_topics[2], 0)]
        :return:
        """
        # self.client.subscribe([(self.mqtt_topics[0], 2), (self.mqtt_topics[1], 1), (self.mqtt_topics[2], 0)])
        while not self.connected:
            getLogger(__name__).debug("Client not connected yet, waiting for CONNACK. . .")
            time.sleep(0.5)
        else:
            getLogger(__name__).debug(f"Subscribed to topic: {topics}")
            self.client.subscribe(topic=topics)

    def pub_topic(self, topic, message):
        while not self.connected:
            pass
        else:
            getLogger(__name__).debug(f'Publish topic: {topic} with data {message}')
            self.client.publish(topic=topic, payload=message)

    def disconnect_client(self):
        self.client.disconnect()
        self.client.loop_stop()
        getLogger(__name__).debug("Client disconnected from broker and stopped runner")
