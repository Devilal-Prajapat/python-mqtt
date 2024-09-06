import paho.mqtt.client as mqtt
import ssl
from time import sleep
from datetime import datetime as dt
import json
import random

client = None
PUB_TOPIC = "demo/pub"
SUB_TOPIC = "demo/sub"

# MQTT_HOST = "broker.hivemq.com"
MQTT_HOST = "test.mosquitto.org"
MQTT_PORT = 1883


def PublishToTopic(pubtopic:str,msg,qos=1):
    global client
    try:
        json_msg = msg #json.loads(msg)
        client.publish(pubtopic,json_msg, qos = qos)  
    except Exception as e:
        print(f"PublishToTopic exception:{e}")

def SubscribeToTopic(topic, qos = 0):
    global client
    try:
        client.subscribe(topic=topic, qos = qos)
    except Exception as e:
        print(f"SubscribeToTopic exception:{e}")


# This callback are now in application code 
def is_json_key_present(json, key):
    try:
        buf = json[key]
    except Exception as e:
        print("Key Error {e}")
        return False
    return True

def handle_incomming_msg(msg):
    try:
        json_msg = json.loads(msg)
    except Exception as e:
        print(f"Json Decode Error {e}")
        return

    if is_json_key_present(json_msg, "led"):
        print("led state {}".format(json_msg["led"]))
    
def on_connect_cb(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    SubscribeToTopic(topic=SUB_TOPIC,qos = 0)

def on_disconnect_cb(client, userdata, rc):
    print("disconect call back")
    MQTTConnect(MQTT_HOST,MQTT_PORT)

def on_message_cb(client, userdata, message, properties=None):
    handle_incomming_msg(message.payload)
    print(
        f"{dt.now()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}"
    )
    #handle_incomming_msg(message.payload)

def on_subscribe_cb(client, userdata, mid, qos, properties=None):
    print(f"{dt.now()} Subscribed with QoS {qos}")


def MQTTInit(on_connect_cb, on_disconnect_cb, on_message_cb, on_subscribe_cb, USE_SSL= 0):
    global client
    clientId = f"IOT-Thing-{str(random.randint(1, 1000000))}"
    print(clientId)
    client = mqtt.Client(client_id=clientId, clean_session=True)
    '''
    client.on_connect = on_connect_cb
    client.on_disconnect = on_disconnect_cb
    client.on_message = on_message_cb
    client.on_subscribe = on_subscribe_cb 
    '''

    client.on_connect = on_connect_cb
    client.on_disconnect = on_disconnect_cb
    client.on_message = on_message_cb
    client.on_subscribe = on_subscribe_cb
    #tls_set(ca_certs: str | None = None, certfile: str | None = None, keyfile: str | None = None, cert_reqs: VerifyMode | None = None, tls_version: int | None = None, ciphers: str | None = None, keyfile_password: str | None = None, alpn_protocols: list[str] | None = None) → 
    if USE_SSL:
        client.tls_set(ca_certs="certs/aws_root_ca.pem",
                certfile ="certs/client.crt",
                keyfile="certs/private.key")

def MQTTConnect(mqtt_host, mqtt_port):
    global client
    client.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
    client.loop_start()

def MQTTDisconnect():
     global client
     client.loop_stop()

if __name__ == "__main__":
    MQTTInit(on_connect_cb, on_disconnect_cb, on_message_cb, on_subscribe_cb,USE_SSL=False)
    MQTTConnect(MQTT_HOST, MQTT_PORT)
    count = 0
    state = True
    while True:
        count += 1
        msg = {"temp": 50, "count": count,"led":state }
        state = not(state)
        json_msg = json.dumps(msg)
        PublishToTopic(PUB_TOPIC,json_msg,qos = 1)  
        sleep(10)
    MQTTDisconnect()
