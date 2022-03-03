import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import yaml
import logging.config
import uuid
import datetime
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
import json
from base import Base

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger("audit")

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

user = app_config.get("datastore")["user"]
password = app_config.get("datastore")["password"]
hostname = app_config.get("datastore")["hostname"]
port = app_config.get("datastore")["port"]
db = app_config.get("datastore")["db"]

DB_ENGINE = create_engine(
    'mysql+pymysql://{}:{}@{}:{}/{}'.format(user, password, hostname, port, db))

Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)


def get_coffeeLocation_readings(index):
    """ Get location Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving location at index %d" % index)
    counter = 1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "event2":
                counter += 1
                if counter == index:
                    return msg, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find location at index %d" % index)
    return {"message": "Not Found"}, 404


def get_coffeeFlavour_readings(index):
    """ Get location Reading in History """
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(
        reset_offset_on_start=True, consumer_timeout_ms=1000)
    logger.info("Retrieving flavour at index %d" % index)
    counter = 1
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == "event1":
                counter += 1
                if counter == index:
                    return msg, 200

    except:
        logger.error("No more messages found")

    logger.error("Could not find location at index %d" % index)
    return {"message": "Not Found"}, 404


app = connexion.FlaskApp(__name__, specification_dir='./')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=9010)