import paho.mqtt.client as mqtt
import ssl
from time import sleep
from datetime import datetime as dt
import json


pub_topic = "rpi/pub"
sub_topic = "rpi/sub"
mqtt_host = ""
mqtt_port = 8883


def is_json_key_present(json, key):
    try:
        buf = json[key]
    except KeyError:
        return False
    return True

def handle_incomming_msg(msg):
    json_msg = json.loads(msg)

    if is_json_key_present(json_msg, "led"):
        print("led state {}".format(json_msg["led"]))

    
def on_connect(client, userdata, flags, reason_code, properties=None):
    print(f"Connected with result code {reason_code}")
    client.subscribe(topic=pub_topic)

def on_disconnect(client, userdata, rc):
    print("disconect call back")

def on_message(client, userdata, message, properties=None):
    handle_incomming_msg(message.payload)
    print(
        f"{dt.now()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}"
    )
    #handle_incomming_msg(message.payload)

def on_subscribe(client, userdata, mid, qos, properties=None):
    print(f"{dt.now()} Subscribed with QoS {qos}")

client = mqtt.Client(client_id="clientid",callback_api_version=mqtt.CallbackAPIVersion.VERSION1, clean_session=True)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message
client.on_subscribe = on_subscribe
#tls_set(ca_certs: str | None = None, certfile: str | None = None, keyfile: str | None = None, cert_reqs: VerifyMode | None = None, tls_version: int | None = None, ciphers: str | None = None, keyfile_password: str | None = None, alpn_protocols: list[str] | None = None) → 
client.tls_set(ca_certs="certs/aws_root_ca.pem",
               certfile ="certs/client.crt",
               keyfile="certs/client.key")
client.connect(host=mqtt_host, port=mqtt_port, keepalive=60)
client.loop_start()
count = 0
state = True
while True:
    count += 1
    msg = {"temp": 50, "count": count,"led":state }
    state = not(state)
    json_msg = json.dumps(msg)
    client.publish(pub_topic,json_msg,qos = 1)  
    sleep(1)
client.loop_stop()
