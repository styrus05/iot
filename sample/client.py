import sys
import ssl
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import json
import time

# Enter your thing name from AWS IoT Core. This must match the thing name you have created because security policy attached to thing only allows connecting to the thing id.
thingName = 'RPi-2'

# Enter your certificate id. This is the topic on which client will be publishing message. Security policy attached to the thing restricts publishing to topic by CertificateId.
certificateId = 'your-certificate-id-goes-here'

mqttc = AWSIoTMQTTClient(thingName)
# Make sure you use the correct endpoint for the region. You can find the endpoint url from the Settings page in the left menu in AWS IoT Core.
mqttc.configureEndpoint("data.iot.us-west-2.amazonaws.com", 8883)

# Provide correct path to the certificate and private key
mqttc.configureCredentials(
    "./rootCA.pem", "./privateKey.pem", "./certificate.pem")

# Prepare the message that you want to publish to AWS IoT. You can add additional attributes here.
message = {
    'source': thingName,
    'message': "this is the sample message from " + thingName
}

# Encoding into JSON
message = json.dumps(message)


# Connect to the AWS IoT Gateway
try:
    mqttc.connect()
    print "Connected to AWS IoT"
except:
    print "Couldn't connect to AWS IoT. Check connection details."
    exit(0)

# Send message to the IOT Topic
while True:
    try:
        # calling publish with Quality of Service (QOS) of 0 wouldn't raise any exception even if you publish to a wrong topic.
        # calling publish with QOS of 1 means "at least once delivery" and generates exception which can be handled on the client side
        # QOS is explained here https://docs.aws.amazon.com/iot/latest/developerguide/mqtt.html
        mqttc.publish(certificateId, message, 1)
        print "Message Published to AWS IoT topic " + certificateId
    except:
        print "Error publishing to the topic " + certificateId
        exit(0)
    time.sleep(5)

mqttc.disconnect()
# To check and see if your message was published to the message broker go to the MQTT Client and subscribe to the iot topic and you should see your JSON Payload
