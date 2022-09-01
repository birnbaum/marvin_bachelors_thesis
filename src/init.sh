#!/bin/bash

chmod 755 .config/rc.local
chmod 755 .config/config.txt
cp .config/rc.local /etc/rc.local
cp .config/config.txt /boot/config.txt
