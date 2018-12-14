import os
import boto3
import psycopg2
import sys

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import json

def main():
    person_key_schema = avro.load('schema/PersonKey.avsc')
    person_schema = avro.load('schema/Person.avsc')

    person_key = {"customerId": "4"}
    #person_value = {"customer-id": "1", "firstName": "Chris", "lastName": "Brown", "birthDate": 1}
    person_value = {"customerId": "4", "firstName": "Chris", "lastName": "Brown"}

    avroProducer = AvroProducer({
        'bootstrap.servers': 'localhost:9092', 'schema.registry.url': 'http://localhost:8082'},
        default_key_schema=person_key_schema,
        default_value_schema=person_schema)

    avroProducer.produce(topic='person', value=person_value, key=person_key)
    avroProducer.flush()

if __name__ == '__main__':
    main()