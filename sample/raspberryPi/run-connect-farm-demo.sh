#!/bin/bash

python3 /home/pi/Documents/code/iot/sample/raspberryPi/farm-sensor-demo.py \
--endpoint a3ng4y5jnf3dy-ats.iot.us-west-2.amazonaws.com \
--root-ca /home/pi/Documents/iot/config/keys/rootCA.pem \
--cert /home/pi/Documents/iot/config/keys/certificate.pem.crt \
--key /home/pi/Documents/iot/config/keys/private.pem.key \
--topic=macdonald/sensor/rpi-B456/command --client-id=macdonald/sensor/rpi-B456/