#!/bin/bash  
sudo cp /home/pi/Documents/iot/config/rpiScanner.service /etc/systemd/system/
sudo systemctl daemon-reload
systemctl stop rpiScanner
sudo systemctl start rpiScanner
sudo systemctl enable rpiScanner