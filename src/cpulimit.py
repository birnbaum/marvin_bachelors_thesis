#!/usr/bin/env python3

import sys
import time
import subprocess
import psutil
from lib import SDL_Pi_SunControl as sdl

def terminate(parent):
    children = parent.children(recursive=True)
    for child in children:
        child.terminate()
    # wait until terminated
    gonealive = psutil.wait_procs(children, timeout=3)
    # if child doesn't terminate, kill
    for child in gonealive[1]:
        child.kill()
    parent.terminate()
    # return codes >= 0 imply termination
    if parent.wait(timeout=3) < 0:
        parent.kill()

def gather_data(parent, output_file):
    for limit in range(50, 401, 50):
        subprocess.run(['sudo', 'cpulimit', '-p', str(parent.pid), '-l', str(limit), '-i'])
        time.sleep(3)
        currents = []
        starttime = time.time()
        while time.time() - starttime < 5:
            currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
            time.sleep(.1)
        # append (cputime,current) to file
        with open(output_file, 'a') as file:
            file.write(f'{limit:}\n')
            for cputime, current in enumerate(currents):
                file.write(f'({(cputime + 1)/10},{current})\n')

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

gather_data(parent, 'cpulimit_currents')
terminate(parent)
