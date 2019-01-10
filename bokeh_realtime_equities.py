from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource
from bokeh.io import curdoc
import numpy as np
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from datetime import datetime

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
        print('no messages')
        return

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        return

    print(msg.value())

    # put messages into a pandas df here
    #prices_df["date"] = msg.value()["time_stamp"]
    #prices_df["close"] = msg.value()["close"]

    #consumer.close()
    return msg


def update_data():
    print('getting data')
    message = get_data()
    #new_data = dict(x=[prices_df["date"]], y=[prices_df["close"]])
    datetime_object = datetime.strptime(message.value()["time_stamp"], '%Y-%m-%d T%H:%M:%S')
    new_data = dict(x=[datetime_object], y=[message.value()["close"]])
    print(new_data)
    source.stream(new_data, 1000)
    return


fig = Figure(plot_width=800,
                    plot_height=400,
                    x_axis_type='datetime',
                    title="Real-Time Price Plot")
fig.line(source=source, x='x', y='y',line_width=2,alpha=.85, color='blue')
fig.xaxis.axis_label = "Date"
fig.yaxis.axis_label = "Disney Real-Time Closing Prices($)"

# show the results
curdoc().add_root(fig)
curdoc().title = "Real-Time Price Plotting from Quandl data"
curdoc().add_periodic_callback(update_data, 100)


