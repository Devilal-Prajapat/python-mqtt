import paho.mqtt.client as mqtt

host = "localhost"
port = 1883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+ str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("hello")

# The callback for when a PUBLISH message is received from the server.
def on_publish(client, userdata, mid):
    print("data published with msg id " + str(mid))

def on_disconnect(client, userdata, rc):
    print("disconnected with result code "+ str(rc))

client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish
client.on_disconnect = on_disconnect

client.username_pw_set(username="devilal",password="123456")
client.connect(host, port, 60)
client.publish("hello","welcome from python")  
client.disconnect()
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()
