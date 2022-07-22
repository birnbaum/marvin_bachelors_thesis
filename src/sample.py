#!/usr/bin/env python3

import sys
import subprocess
import time
import statistics
import SDL_Pi_SunControl

# argv
server_address = sys.argv[1]

# config
sunControl = SDL_Pi_SunControl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
)

for cpus in range(4, 0, -1):
    subprocess.run(
            ['./build_image.sh', '--build-arg', 'BASE_IMAGE_TYPE=cpu'],
            cwd='flwr_pi'
    )
    starttime = time.time()
    docker_instance = subprocess.Popen(
            ['docker', 'run', '--cpus="' + str(cpus) + '"','--rm', 'flower_client',
            '--server_address=' + server_address, '--cid=0', '--model=Net'],
            cwd='flwr_pi'
    )

    # check every second if docker_instance has terminated
    currents = []
    while (docker_instance.poll() == None):
        currents.append(sunControl.readChannelCurrentmA(SDL_Pi_SunControl.SunControl_OUTPUT_CHANNEL))
        time.sleep(1)

    # docker_instance has terminated
    endtime = time.time()
    # append (cpus,cputime) and (median_current,cputime) to file
    cputime = endtime - starttime
    median_current = statistics.median(currents)
    f = open('data', 'a')
    f.write(f'({cpus},{cputime})({median_current:3.2f},{cputime})\n')
    f.close()
