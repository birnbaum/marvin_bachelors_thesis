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

def gather_data(parent, freqs, output_file):
    # only the userspace governor can force the cores to run at specific frequency
    subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'userspace'])
    for freq in freqs:
        means = []
        # set specific frequency to use
        subprocess.run(['sudo', 'cpupower', 'frequency-set', '-f', str(freq * 1000)])
        time.sleep(2)
        for cpulimit in range(50, 401, 50):
            currents = []
            # only use 50 - 400% of cpu (100% per core)
            cpulimit_process = subprocess.Popen(['cpulimit', '-p', str(parent.pid), '-l', str(cpulimit), '-i'])
            starttime = time.time()
            # gather currents for 2 minutes
            while time.time() - starttime < 120:
                currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
                time.sleep(1)
            cpulimit_process.kill()
            means.append(statistics.mean(currents))
        with open(output_file, 'a') as file:
            file.write('\\addplot\ncoordinates {\n')
            for index, mean in enumerate(means):
                cpulimit = (index + 1) * 50
                file.write(f'({cpulimit},{mean:3.2f})\n')
            file.write(f'}};\n\\addlegendentry{{{freq}}}\n')
    # return to default governor ondemand
    subprocess.run(['sudo', 'cpupower', 'frequency-set', '-g', 'ondemand'])

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

gather_data(parent, freqs, 'freqs_cpulimit_currents')
kill_family(parent)
