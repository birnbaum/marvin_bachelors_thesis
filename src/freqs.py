#!/usr/bin/env python3

import sys
import time
import statistics
import subprocess
import psutil
from lib import SDL_Pi_SunControl as sdl

def kill_family(parent):
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()

def gather_data(freqs, output_file):
    # only the userspace governor can force the cores to run at specific frequency
    subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'userspace'])
    means = []
    for freq in freqs:
        # set specific frequency to use
        subprocess.run(['sudo', 'cpupower', 'frequency-set', '-f', str(freq * 1000)])
        time.sleep(3)
        currents = []
        starttime = time.time()
        # gather currents for 2 minutes
        while time.time() - starttime < 120:
            currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
            time.sleep(1)
        means.append(statistics.mean(currents))
        # append (cputime,current) to file
        with open(output_file, 'a') as file:
            for cputime, current in enumerate(currents):
                file.write(f'({cputime + 1},{current:3.2f})\n')
            file.write('\n')
    # return to default governor ondemand
    subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'ondemand'])
    # save gathered mean values
    with open(output_file, 'a') as file:
        for mean in means:
            file.write(f'{mean}\n')

# argv
pid_parent = int(sys.argv[1])
parent = psutil.Process(pid_parent)

# suncontrol config
sc = sdl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
)

# available frequencies for Raspberry Pi 3b+
freqs = [600, 700, 800, 900, 1000, 1100, 1200]

gather_data(freqs, 'freq_currents_load')
kill_family(parent)
