# How to run the samples on a Raspberry Pi?

1. install AWS IOT SDK for python (python 3.5+ required)
   pip install awsiotsdk
   or pip3 install awsiotsdk (if pip3 fails, check if you have a latest version of pip by pressing tab after pip and using he most latest version which is greate 3.5)

If issues with installation - check https://github.com/aws/aws-iot-device-sdk-python-v2 for instructions

Note: if you have sense Hat installed on your pi, also install
pip3 install sense-hat

2. Register a thing in AWS IoT Core and associate certificate and policy (Refer to policyExamples/secure-by-thingName.json for example policy).

3. Store the certificate in a secure location on your raspberry pi

4. Publish message to a topic starting with thing name

python3 publish.py --endpoint your-aws-iot-core-endpoint --root-ca path-for-rootCA-file --cert path-for-certificate-file --key path-for-private-key-file --message '{"message":"hello"}' --topic=it-must-match-your-thing-name/scan --count=10 --client-id=it-must-match-your-thing-name

5. Subscribe message from a topic starting with thing name

python3 subscribe.py --endpoint your-aws-iot-core-endpoint --root-ca path-for-rootCA-file --cert path-for-certificate-file --key path-for-private-key-file --topic=it-must-match-your-thing-name/scan --client-id=it-must-match-your-thing-name

Note: Subscribe code looks for message in format {"message":"hello"} and displays message attribute from payload on sensehat LED.

6. Optional steps to add the subscribe.py as a daemon
   - follow the instructions listed here https://www.raspberrypi.org/documentation/linux/usage/systemd.md
   - Note: don't use ~ in the path, use absolute path /home/pi/Documents/code instead of ~/Documents/code
   - Note: provide the working directory where the code file (subscribe.py).
   - a sample service file is available in rpiScanner.service
   - edit the file to put the correct certificate path
   - then copy this file in /etc/systemd/system/ folder
     sudo cp rpiScanner.service /etc/systemd/system/rpiScanner.service
   - test by starting the daemon process
     sudo systemctl start rpiScanner.service
   - once tested successfully, enable it by
     sudo systemctl enable rpiScanner.service
   - To CHECK logs for the daemon process if there are errors - journalctl -u rpiScanner.service -b
   - sudo systemctl status rpiScanner.service to check the status of the service
