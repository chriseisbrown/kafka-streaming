# Stock prices onto Kafka
Assuming Cloudera and base Kafka distibutions are installed in development directory:

Mainly using the base distribution but schema registry is a Confluent product so will need 
to have that installed.

![]('./Kafka-Bokeh streaming - architecture.png')


cd development/kafka-2.11/kafka_2.12-2.1.0

####start zookeeper:
bin/zookeeper-server-start.sh config/zookeeper.properties

###start kafka:
bin/kafka-server-start.sh config/server.properties



#### make a topic:
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test

#### put some test data on it:
seq 100 | bin/kafka-console-producer.sh --broker-list localhost:9092 --topic test


cd development/confluent-kafka/confluent-5.0.1

####start schema registry:
bin/schema-registry-start etc/schema-registry/schema-registry-dev.properties


####start confluence-control-center:
bin/control-center-start etc/confluent-control-center/control-center-dev.properties

open browser on localhost:9021 to see control center

run person_loader.py to register a schema and put a message onto topic 


####start KSQL:
````bin/ksql-server-start etc/ksql/ksql-server.properties````

run a KQSL client by opening a new terminal and typing: 

````bin/ksql http://localhost:8088````


#### ask schema-registry to tell you what subjects it has:
curl -X GET http://localhost:8082/subjects
#### show what schema versions are in a subject
curl -X GET http://localhost:8082/subjects/person-value/versions
#### show me version 1 of the schema in the subject
curl -X GET http://localhost:8082/subjects/person-value/versions/1

## install Quandl
... into your virtualenv.  
```
pip install quandl
```

## load the Kafka topic with prices
run equity_price_loader.py.  This will take end of day stock price data from 
quandl and post events onto the kafka topic equity_<stock ticker>, e.g.; the topic 
will be called equity_DIS if Walt Disney stock prices are being used. 

The initial schema definition for the price event looks like this;

```json
{
  "type": "record",
  "name": "EquityPrice",
  "namespace": "com.comparethemarket.kafkastreaming",
  "fields": [
    {
      "name": "ticker_symbol",
      "type": "string"
    },
    {
      "name": "time_stamp",
      "type": "string",
      "logicalType" : "timestamp-millis"
    },
    {
      "name": "close",
      "type": "double"
    }
  ]
}
```
If you run something like this from a command line:
```
curl -X GET http://localhost:8082/subjects/equity_DIS-value/versions/1
```
you will see the schema registry send back something that looks very similar to the schema above.  

## check the compatibility setting of your schemas
Run this:
```
curl -X GET http://localhost:8082/config
```

and you should see
```{"compatibilityLevel":"BACKWARD"}```

this shows us that the compatibility mode that the registry will try and enforce is backwards.
Any modifications we make to the EquityPrice schema will have to allow for the new schema (version 2) 
to be able to read events that were put on Kafka using the previous version (version 1).

It will be good to have the stock's open price in the price event as well.  Open schema/equityPrice.avsc
and change the json to look like this;

```json
{
  "type": "record",
  "name": "EquityPrice",
  "namespace": "com.comparethemarket.kafkastreaming",
  "fields": [
    {
      "name": "ticker_symbol",
      "type": "string"
    },
    {
      "name": "time_stamp",
      "type": "string",
      "logicalType" : "timestamp-millis"
    },
    {
      "name": "close",
      "type": "double"
    },
    {
      "name": "open",
      "type": "double"
    }
  ]
}
```

If you run equity_price_loader.py again it will fail with this error message:
```
confluent_kafka.avro.error.ClientError: Incompatible Avro schema:409
```

This is because we are trying to add a new field for the open price but events made with
the old schema wouldn't have been created with an 'open' field.  What we're trying to
 do to the schema is not backwards compatible.

Any code trying to use the version 2 schema to look at old events won't find the 
'open' field.  Effectively we are about to break the contract 
that the version 2 schema would promise if it were allowed to exist.

## Check that price data events can be consumed from the topic
Run equity_price_consumer.py.  This is a simple AvroConsumer that will read from the equity_DIS topic and display 
the messages it finds in the console.

## Run the realtime plotting script
Run the bokeh plot script bokeh_realtime_equities.py.  Make sure you have activated 
the virtualenv that bokeh has been installed in.
``` cd virtual_envs/py_3_6_2
source bin/activate

cd development/python/kafka-streaming
bokeh serve bokeh_realtime_equities.py 
```
Open a browser at http://localhost:5006/bokeh_realtime_equities

run equity_price_loader.py to load stock prices onto the Kafka



give props to 
https://zduey.github.io/snippets/streaming-stock-data-with-bokeh/
https://towardsdatascience.com/stock-prediction-in-python-b66555171a2
https://medium.com/python-data/quandl-getting-end-of-day-stock-data-with-python-8652671d6661


