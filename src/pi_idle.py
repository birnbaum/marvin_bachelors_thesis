#!/usr/bin/env python3

import time
import statistics
import SDL_Pi_SunControl as sdl

# config
sc = sdl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
)

starttime = time.time()
# get every 5 seconds idle current
currents = []
while cputime := time.time() - starttime < 60:
    currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
    # append (current,cputime) to file
    with open('idle_currents', 'a') as f:
        f.write(f'({currents[-1]},{cputime})\n')
    time.sleep(5)
mean_current = statistics.mean(currents)
print(f'Measured a mean current of {mean_current} over 60 seconds')
