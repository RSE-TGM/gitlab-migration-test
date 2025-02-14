from paho.mqtt import client as paho_mqtt_client

from read_config import mqtt_config

mqtt_client = None
if mqtt_config.BROKER_HOST is not None:
    try:
        mqtt_client = paho_mqtt_client.Client()
        mqtt_client.username_pw_set(username=mqtt_config.CLIENT_USERNAME, password=mqtt_config.CLIENT_PWD)
        mqtt_client.connect(mqtt_config.BROKER_HOST, mqtt_config.BROKER_PORT, 60)
        mqtt_client.loop_start()

    except Exception as e:
        print(e)
