#!/usr/bin/env python3

import sys
import time
import subprocess
import psutil
import SDL_Pi_SunControl as sdl

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

def gather_data(freqs, output_file):
    for freq in freqs:
        # set maximum cpu frequency
        subprocess.run(['sudo', 'cpupower', 'frequency-set', '-u', str(freq * 1000)])
        time.sleep(3)
        currents = []
        starttime = time.time()
        # gather currents for 20 seconds
        while time.time() - starttime < 20:
            currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
            time.sleep(1)
        # append (cputime,current) to file
        with open(output_file, 'a') as file:
            file.write(f'{freq}\n')
            for cputime, current in enumerate(currents):
                file.write(f'({cputime + 1},{current})\n')

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
freqs = [600, 700, 800, 900, 1000, 1100, 1200],

gather_data(freqs, 'freq_currents_load')
terminate(parent)
gather_data(freqs, 'freq_currents_idle')
