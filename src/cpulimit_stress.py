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

def gather_data(parent, output_file):
    means = []
    for cpulimit in range(50, 401, 50):
        cpulimit_process = subprocess.Popen(['cpulimit', '-p', str(parent.pid), '-l', str(cpulimit), '-i'])
        time.sleep(.5)
        currents = []
        starttime = time.time()
        # gather currents for 2 minutes
        while time.time() - starttime < 120:
            currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
            time.sleep(1)
        # kill cpulimit process
        cpulimit_process.kill()
        means.append(statistics.mean(currents))
        # append (cputime,current) latex usable
        with open(output_file, 'a') as file:
            file.write('\\addplot\ncoordinates {\n')
            for cputime, current in enumerate(currents):
                file.write(f'({cputime + 1},{current:3.2f})\n')
            file.write(f'}};\n\\addlegendentry{{{cpulimit}}}\n')
    # save gathered mean values at end of file
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

gather_data(parent, 'cpulimit_currents_load')
kill_family(parent)
