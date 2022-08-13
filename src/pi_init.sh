#!/bin/bash

ln -sf ./pi_rc.local /etc/rc.local                   # symlink to startup script
ln -sf ./pi_config.txt /boot/config.txt              # symlink to pi_config.txt
echo '1-1' | tee /sys/bus/usb/drivers/usb/unbind    # disable usb
tvservice -o                                        # disable hdmi
