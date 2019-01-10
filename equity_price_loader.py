import quandl
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

QUANDL_API_KEY = "PWzyrA_2u_etidGrAk1j"
EQUITY_TICKER = "DIS"
SERIES_TYPE = "EOD"

SCHEMA_REGISTRY_URL = 'http://localhost:8082'
TOPIC_NAME = "equity_" + EQUITY_TICKER
START_DATE = "2017-12-31"
END_DATE = "2018-12-31"


def main():
    quandl.ApiConfig.api_key = QUANDL_API_KEY
    data = quandl.get(SERIES_TYPE + "/" + EQUITY_TICKER, start_date=START_DATE, end_date=END_DATE)

    print(data.head(5))
    print(data.describe())


    equity_price_key_schema = avro.load('schema/EquityPriceKey.avsc')
    equity_price_schema = avro.load('schema/EquityPrice.avsc')

    avroProducer = AvroProducer({
        'bootstrap.servers': 'localhost:9092', 'schema.registry.url': SCHEMA_REGISTRY_URL},
        default_key_schema=equity_price_key_schema,
        default_value_schema=equity_price_schema)

    for index, row in data.iterrows():
        iso_date = index.strftime('%Y-%m-%d T%H:%M:%S')

        equity_key = {"ticker_symbol": EQUITY_TICKER, "time_stamp" : iso_date}
        equity_value = {"ticker_symbol": EQUITY_TICKER, "time_stamp": iso_date, "close": row['Close']}
        avroProducer.produce(topic=TOPIC_NAME, value=equity_value, key=equity_key)

    avroProducer.flush()

if __name__ == '__main__':
    main()