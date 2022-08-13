#!/bin/bash

cp ./pi_rc.local /etc/rc.local
cp ./pi_config.txt /boot/config.txt
echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind    # disable usb
tvservice -o                                        # disable hdmi
