from bokeh.plotting import Figure
from bokeh.models import ColumnDataSource, HoverTool, ResetTool, SaveTool, BoxZoomTool, ZoomInTool, ZoomOutTool
from bokeh.io import curdoc
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from datetime import datetime
import fbprophet
from pandas import DataFrame

EQUITY_TICKER = "DIS"

SCHEMA_REGISTRY_URL = 'http://localhost:8082'
TOPIC_NAME = "equity_" + EQUITY_TICKER

prices = []
prices_df = DataFrame
source = ColumnDataSource(dict(time=[], hover_time=[], close=[]))

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
        return msg

    if msg.error():
        print("AvroConsumer error: {}".format(msg.error()))
        return msg

    # put messages into a pandas df here
    #prices_df["date"] = msg.value()["time_stamp"]
    #prices_df["close"] = msg.value()["close"]
    #consumer.close()
    print(msg.value())
    prices.append(msg.value())
    return msg


def create_model():
    # Make the model
    daily_seasonality = False
    weekly_seasonality=False
    yearly_seasonality = True
    monthly_seasonality = True
    changepoint_prior_scale = 0.05
    changepoints = None

    model = fbprophet.Prophet(daily_seasonality=daily_seasonality,
                              weekly_seasonality=weekly_seasonality,
                              yearly_seasonality=yearly_seasonality,
                              changepoint_prior_scale=changepoint_prior_scale,
                              changepoints=changepoints)

    if monthly_seasonality:
        # Add monthly seasonality
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)

    return model


def make_price_prediction():
    create_model()


def update_data():
    print('getting data from topic')
    message = get_data()
    if message is None:
        return

    if len(prices) > 240:
        predicted_data = make_price_prediction()

    datetime_object = datetime.strptime(message.value()["time_stamp"], '%Y-%m-%d T%H:%M:%S')
    historic_data = dict(time=[datetime_object], hover_time=[message.value()["time_stamp"]] , close=[message.value()["close"]])
    print(historic_data)
    source.stream(historic_data, 1000)
    return


hover_tool = HoverTool(tooltips=[("Date", "@hover_time"), ("Closing Price", "@close")])

fig = Figure(plot_width=800,
                    plot_height=400,
                    x_axis_type='datetime',
                    tools=[hover_tool, ResetTool(), SaveTool(), BoxZoomTool(), ZoomInTool(), ZoomOutTool()],
                    title="Real-Time Price Plot")
fig.line(source=source, x='time', y='close',line_width=2,alpha=.85, color='blue')
fig.xaxis.axis_label = "Date"
fig.yaxis.axis_label = "Disney Real-Time Closing Prices($)"

# show the results
curdoc().add_root(fig)
curdoc().title = "Real-Time Price Plotting from Quandl data"
curdoc().add_periodic_callback(update_data, 100)


