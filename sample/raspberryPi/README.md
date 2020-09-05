# How to run the samples on Raspberry Pi?

1. install AWS IOT SDK for python (python 3.5+ required)
   pip install awsiotsdk
   or pip3 install awsiotsdk

If issues with installation - check https://github.com/aws/aws-iot-device-sdk-python-v2 for instructions

2. Register a thing in AWS IoT Core and associate certificate and policy to it.

3. To publish to test/topic
   python pubsub.py --endpoint <endpoint> --root-ca <file> --cert <file> --key <file>

4. To subscribe from test/topic
   python subscribe.py --endpoint <endpoint> --root-ca <file> --cert <file> --key <file>
