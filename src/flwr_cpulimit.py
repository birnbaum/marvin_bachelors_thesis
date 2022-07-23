#!/usr/bin/env python3
#
# test pi's energy consumption with different
# resource limitations (via cpulimit)
# usage:
#
# python flwr_pi/server.py --server_address <server_address>:<port> \
# --rounds 1 --min_num_clients 1 --min_sample_size 1 --model Net
#
# python flwr_dockercpus.py <server_address>:<port>

import sys
import subprocess
import time
import statistics
import SDL_Pi_SunControl as sdl

# argv
server_address = sys.argv[1]

# config
sc = sdl.SDL_Pi_SunControl(
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
    docker_instance = subprocess.Popen(
            ['docker', 'run', '--rm', 'flower_client', '--server_address=' +
                server_address, '--cid=0', '--model=Net'],
            cwd='flwr_pi'
    )
    # limit cpu utilization for docker_instance
    subprocess.run(['cpulimit', '-p', str(docker_instance.pid), '-l', str(cpus * 100)])
    starttime = time.time()
    # check every second if docker_instance has terminated
    currents = []
    while (docker_instance.poll() == None):
        currents.append(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))
        time.sleep(1)
    # docker_instance has terminated
    endtime = time.time()
    cputime = int(endtime - starttime)
    mean_current = statistics.mean(currents)
    # append (cpus,cputime)(mean_current,cputime) to file
    with open('data', 'a') as f:
        f.write(f'({cpus},{cputime})({mean_current:3.2f},{cputime})\n')
