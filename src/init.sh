#!/bin/bash

chmod 755 ./pi_rc.local
chmod 755 ./pi_config.txt
cp ./pi_rc.local /etc/rc.local
cp ./pi_config.txt /boot/config.txt
