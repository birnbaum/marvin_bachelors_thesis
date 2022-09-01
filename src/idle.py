#!/usr/bin/env python3

import time
import statistics
from lib import SDL_Pi_SunControl as sdl

# config
sc = sdl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
)

time.sleep(10)
starttime = time.time()
# get every second idle current for 2 minutes
currents = []
while cputime := time.time() - starttime < 120:
    currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
    time.sleep(1)
# append currents and mean to file
with open('idle_currents', 'a') as file:
    for index, current in enumerate(currents):
        file.write(f'({index + 1},{current:3.2f})\n')
    file.write(f'\nmean: {statistics.mean(currents)}')
