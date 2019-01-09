from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
import numpy as np
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

from pandas import DataFrame

EQUITY_TICKER = "DIS"

SCHEMA_REGISTRY_URL = 'http://localhost:8082'
TOPIC_NAME = "equity_" + EQUITY_TICKER


prices_df = DataFrame
source = ColumnDataSource(dict(x=[], y=[]))

consumer = AvroConsumer({
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'groupid',
    'schema.registry.url': SCHEMA_REGISTRY_URL})

consumer.subscribe([TOPIC_NAME])


def get_data():
    try:
        msg = consumer.poll(10)

    except SerializerError as e:
        print("Message deserialization failed for {}: {}".format(msg, e))
        return

    if msg is None:
        return

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        return

    print(msg.value())

    # put messages into a pandas df here
    prices_df["date"] = msg.value()["time_stamp"]
    prices_df["close"] = msg.value()["close"]

    #consumer.close()


def update_data():
    get_data()
    new_data = dict(x=[prices_df["date"]], y=[prices_df["close"]])
    source.stream(new_data, 1000)


def main():
    fig = Figure()
    fig.line(source=source, x='x', y='y', line_width=2, alpha=.85, color='red')
    #fig.line(source=source, x='x', y='avg', line_width=2, alpha=.85, color='blue')

    # prepare some data


    # show the results
    curdoc().add_root(fig)
    curdoc().add_periodic_callback(update_data, 100)

if __name__ == '__main__':
    main()
