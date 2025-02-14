from typing import List
import time
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from pyModbusTCP.client import ModbusClient
from read_config import db_config, modbus_config, mqtt_config, logging

from models import modbus_devices
from factory_clients import mqtt_client

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info(" Launching modbus application ...")

    try:

        mb_device = modbus_devices[modbus_config.DEVICE]()
        RG_START = int(mb_device.register_start)
        RG_LEN = int(mb_device.register_length)

        modbus_client = ModbusClient(
            host=modbus_config.HOST,
            port=modbus_config.PORT,
            unit_id=1,
            debug=False
        )
        modbus_client.open()
        if not modbus_client.is_open:
            raise ConnectionError
        logger.info(" TCP/IP modbus client connected")

        db_url = f"postgresql://{db_config.USER}:{db_config.PWD}@{db_config.HOST}:{db_config.PORT}/{db_config.NAME}"
        engine = create_engine(db_url, echo=False)
        engine.connect()  # if the connection fails it raises the OperationalError
        logger.info(" Database engine connected")

    except KeyError as e:
        raise KeyError(f"KeyError: {e}. MODBUS_DEVICE shall be one of: {modbus_devices.keys()}")

    except ConnectionError:
        err = f"ConnectionError: Modbus client unable to connect to {modbus_config.HOST}:{modbus_config.PORT}"
        raise ConnectionError(err)

    except OperationalError as e:
        err = f"DatabaseConnectionError {e}: Unable to connect to {db_config.HOST}:{db_config.PORT}, {db_config.NAME}"
        raise ConnectionError(err)

    logger.info(f" Start reading modbus data with polling interval {modbus_config.POLLING_INTERVAL}")
    while True:

        time.sleep(modbus_config.POLLING_INTERVAL)

        if modbus_client.is_open:

            regs: List[int] = modbus_client.read_holding_registers(RG_START, RG_LEN)  # aka: modbus function 0x03
            if regs is None:
                logger.warning(" Empty holding register")
                continue

            df: pd.DataFrame = mb_device.convert_registers_to_df_values(regs=regs)
            with engine.begin() as connection:
                logger.debug(f"{df}")
                df.to_sql(db_config.TABLE, con=connection, if_exists="append", index=False)

            try:
                mqtt_client.publish(mqtt_config.TOPIC, df.to_dict(), mqtt_config.QOS)
            except Exception:
                mqtt_client.connect()
                pass

        else:
            logger.warning(f" Connection to modbus server {modbus_config.HOST}:{modbus_config.PORT} lost. RETRY")
            modbus_client.open()
