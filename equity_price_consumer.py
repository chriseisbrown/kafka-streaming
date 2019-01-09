from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

EQUITY_TICKER = "DIS"

SCHEMA_REGISTRY_URL = 'http://localhost:8082'
TOPIC_NAME = "equity_" + EQUITY_TICKER

consumer = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'groupid',
    'schema.registry.url': SCHEMA_REGISTRY_URL})

consumer.subscribe([TOPIC_NAME])

while True:
    try:
        msg = consumer.poll(10)

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        break

    if msg is None:
        continue

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        continue

    print(msg.value())

consumer.close()