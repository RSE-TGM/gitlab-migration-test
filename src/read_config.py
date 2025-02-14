import os
import logging
from collections import namedtuple
from dotenv import load_dotenv

DBConfig = namedtuple('DBConfig', 'HOST, PORT, NAME, USER, PWD, TABLE')
ModbusConfig = namedtuple('ModbusConfig', 'HOST, PORT, DEVICE, POLLING_INTERVAL')
MQTTConfig = namedtuple('MQTTConfig', 'BROKER_HOST, BROKER_PORT, CLIENT_USERNAME, CLIENT_PWD, TOPIC, QOS')

load_dotenv()

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)
logger.info(f" Setting logger with LOG_LEVEL: {os.environ.get('LOG_LEVEL', 'INFO')}")


db_config = DBConfig(
    HOST=os.environ["DB_HOST"],
    PORT=int(os.environ["DB_PORT"]),
    USER=os.environ["DB_USER"],
    PWD=os.environ["DB_PWD"],
    NAME=os.environ["DB_NAME"],
    TABLE=os.environ["DB_TABLE"],
)

modbus_config = ModbusConfig(
    HOST=os.environ["MODBUS_HOST"],
    PORT=int(os.environ["MODBUS_PORT"]),
    DEVICE=os.environ["MODBUS_DEVICE"],
    POLLING_INTERVAL=int(os.environ["MODBUS_POLLING_INTERVAL"])
)

mqtt_config = MQTTConfig(
    BROKER_HOST=os.environ["BROKER_HOST"],
    BROKER_PORT=int(os.environ["BROKER_PORT"]),
    CLIENT_USERNAME=os.environ["MQTT_USERNAME"],
    CLIENT_PWD=os.environ["MQTT_PWD"],
    TOPIC=os.environ["MQTT_TOPIC"],
    QOS=int(os.environ["MQTT_QOS"]),
)
