# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.
# A sample example of subscribe
from __future__ import absolute_import
from __future__ import print_function
import argparse
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import sys
import threading
import time
from time import sleep
from random import randint
from datetime import datetime


from uuid import uuid4

import json
import subprocess
try:
    from sense_hat import SenseHat
    sense = SenseHat()
except:
    print("sense hat module not found")

# This sample uses the Message Broker for AWS IoT to send and receive messages
# through an MQTT connection. On startup, the device connects to the server,
# subscribes to a topic, and begins publishing messages to that topic.
# The device should receive those same messages back from the message broker,
# since it is subscribed to that same topic.

parser = argparse.ArgumentParser(
    description="Send and receive messages through and MQTT connection.")
parser.add_argument(
    '--endpoint',
    required=True,
    help="Your AWS IoT custom endpoint, not including a port. " +
    "Ex: \"abcd123456wxyz-ats.iot.us-east-1.amazonaws.com\"")
parser.add_argument(
    '--cert', help="File path to your client certificate, in PEM format.")
parser.add_argument('--key',
                    help="File path to your private key, in PEM format.")
parser.add_argument(
    '--root-ca',
    help="File path to root certificate authority, in PEM format. " +
    "Necessary if MQTT server uses a certificate that's not already in " +
    "your trust store.")
parser.add_argument('--client-id',
                    default="test-" + str(uuid4()),
                    help="Client ID for MQTT connection.")
parser.add_argument('--topic',
                    default="test/topic",
                    help="Topic to subscribe to, and publish messages to.")
parser.add_argument('--message',
                    default="Hello World!",
                    help="Message to publish. " +
                    "Specify empty string to publish nothing.")
parser.add_argument(
    '--count',
    default=10,
    type=int,
    help="Number of messages to publish/receive before exiting. " +
    "Specify 0 to run forever.")
parser.add_argument(
    '--use-websocket',
    default=False,
    action='store_true',
    help="To use a websocket instead of raw mqtt. If you " +
    "specify this option you must specify a region for signing, you can also enable proxy mode."
)
parser.add_argument(
    '--signing-region',
    default='us-east-1',
    help="If you specify --use-web-socket, this " +
    "is the region that will be used for computing the Sigv4 signature")
parser.add_argument(
    '--proxy-host',
    help="Hostname for proxy to connect to. Note: if you use this feature, " +
    "you will likely need to set --root-ca to the ca for your proxy.")
parser.add_argument('--proxy-port',
                    type=int,
                    default=8080,
                    help="Port for proxy to connect to.")
parser.add_argument('--verbosity',
                    choices=[x.name for x in io.LogLevel],
                    default=io.LogLevel.NoLogs.name,
                    help='Logging level')

# Using globals to simplify sample code
args = parser.parse_args()

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')

received_count = 0
received_all_event = threading.Event()

# Callback when connection is accidentally lost.


def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(
        return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

# Define function to collect weather data
def get_weather(sensor_id, id):
    temperature = float(sense.get_temperature() * (9 / 5) + 32)
    humidity = float(sense.get_humidity())
    pressure = float(sense.get_pressure())
    timestamp = str(datetime.now())

    weather = {'ID': id, 'SensorID': sensor_id, 'Temperature': temperature, 'Humidity': humidity, 'Pressure': pressure, 'Timestamp': timestamp}
    return weather


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    print("Received message from topic '{}': {}".format(topic, payload))
    global received_count

    # convert byte to string
    payloadString = payload.decode('utf-8')
    # print(payloadString)

    # convert string to json
    payloadJson = json.loads(payloadString)

    # print received message
    # display message on senseHat LED
    if (payloadJson['message'].upper() == 'SET'):
        try:
            #hex_color = '123456'
            hex_color = payloadJson['color']
            RGB_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            #print(RGB_color)
            sense.clear(RGB_color[0],RGB_color[1],RGB_color[2])
        except:
            print(payloadString)            
    elif (payloadJson['message'].upper() == 'ON'):
        try:
            sense.clear(255, 255, 255)
        except:
            print(payloadString)

    elif (payloadJson['message'].upper() == 'OFF'):
        try:
            sense.clear(0, 0, 0)
        except:
            print(payloadString)

    else:
        if (payloadJson['message'].upper() == 'SPARKLE'):
            try:
                j = 0
                i = 0
                sense.clear()
                while i < 2:
                    x = randint(0, 7)
                    y = randint(0, 7)
                    r = randint(0, 255)
                    g = randint(0, 255)
                    b = randint(0, 255)
                    sense.set_pixel(x, y, r, g, b)
                    j = j + 1
                    sleep(0.01)
                    if (j == 50):
                        sense.clear(255, 255, 255)
                        sleep(0.3)
                        sense.clear(255, 0, 0)
                        sleep(0.3)
                        sense.clear(0, 255, 0)
                        sleep(0.3)
                        sense.clear(0, 0, 255)
                        j = 0
                        i = i + 1
                sense.clear(0, 0, 0)
            except:
                print(payloadString)
        else:
            try:
                sense.show_message(payloadJson['message'],
                                   text_colour=[255, 0, 0])
            except:
                print(payloadString)

    # received_count += 1
    # if received_count == args.count:
    #	received_all_event.set()


if __name__ == '__main__':
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    if args.use_websocket == True:
        proxy_options = None
        if (args.proxy_host):
            proxy_options = http.HttpProxyOptions(host_name=args.proxy_host,
                                                  port=args.proxy_port)

        credentials_provider = auth.AwsCredentialsProvider.new_default_chain(
            client_bootstrap)
        mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=args.endpoint,
            client_bootstrap=client_bootstrap,
            region=args.signing_region,
            credentials_provider=credentials_provider,
            websocket_proxy_options=proxy_options,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=6)

    else:
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=args.endpoint,
            cert_filepath=args.cert,
            pri_key_filepath=args.key,
            client_bootstrap=client_bootstrap,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=6)

    print("Connecting to {} with client ID '{}'...".format(
        args.endpoint, args.client_id))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))

    # Publish message to server desired number of times.
    # This step is skipped if message is blank.
    # This step loops forever if count was set to 0.
    
    # Example command topic is office/weather/rpi-B123/command
    command_topic = args.topic

    # get the high-level topic name
    sensor_topic = args.topic.split("/")[0] + "/" + args.topic.split("/")[1]

    # get the sensor id
    sensor_id = args.topic.split("/")[2]

    # sensor_topic = "office/weather"
    id = 0
    metrics = ['Temperature', 'Humidity', 'Pressure']
    if args.message:
        if args.count == 0:
            print ("Sending messages until program killed")
        else:
            print ("Sending {} message(s)".format(args.count))

        publish_count = 1
        while (publish_count <= args.count) or (args.count == 0):
            for metric in metrics:
                data = {key: get_weather(sensor_id, id)[key] for key in (metric, 'ID', 'SensorID', 'Timestamp')}
                sub_topic = sensor_topic.split('/')[0] + '/metrics/' + metric
                mqtt_connection.publish(topic=sub_topic, payload=json.dumps(data), qos=mqtt.QoS.AT_LEAST_ONCE)
                print('The ' + metric + ' recorded is ' + str(data[metric]) + '. Published message on '
                                                                                                'topic ' + sub_topic)
            #mqtt_connection.publish(sensor_topic, json.dumps(get_weather(id)), config.QOS_LEVEL)
            mqtt_connection.publish(topic=sensor_topic, payload=json.dumps(get_weather(sensor_id, id)), qos=mqtt.QoS.AT_LEAST_ONCE)
            print('Published message on topic ' + sensor_topic)
            id += 1
            time.sleep(15)

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if args.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print("{} message(s) received.".format(received_count))

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")