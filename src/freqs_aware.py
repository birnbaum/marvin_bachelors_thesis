#!/usr/bin/env python3

from time import sleep
import statistics
import math
from threading import Thread
from cpufreq import cpuFreq
from lib import SDL_Pi_SunControl as sdl

def read_file(file_name):
    with open(file_name) as file:
        return [int(float(line.rstrip())) * 3 for line in file]

def tex_plot(output_file, data, legendentry):
    with open(output_file, 'a') as file:
        file.write('\\addplot\ncoordinates {\n')
        for cputime, current in enumerate(data):
            file.write(f'({cputime + 1},{current})\n')
        file.write(f'}};\n\\addlegendentry{{{legendentry}}}\n')

def pi_current(sc):
    return int(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))

def afterwatch(cpu, sc, should_current, stop):
    currents = []
    for _ in range(0, 5):
        currents.append(pi_current(sc))
        if stop():
            return
        sleep(1)
    mean = statistics.mean(currents)
    freqs = cpu.available_frequencies
    freq_index = freqs.index(cpu.get_frequencies()[0])
    if mean > should_current:
        cpu.set_max_frequencies(freqs[freq_index - 1])
    elif mean < should_current:
        cpu.set_max_frequencies(freqs[freq_index + 1])
    else:
        return

def log_search(cpu, sc, should_current, stop):
    is_current = pi_current(sc)
    freqs = cpu.available_frequencies
    freq_index = freqs.index(cpu.get_frequencies()[0])
    if is_current < should_current:
        L = freq_index
        R = len(freqs) - 1
    elif is_current > should_current:
        L = 0
        R = freq_index
    else:
        return
    while abs(L - R) > 2:
        M = math.ceil((L + R) / 2)
        cpu.set_max_frequencies(freqs[M])
        sleep(5)
        is_current = pi_current(sc)
        if is_current < should_current:
            L = M + 1
        elif is_current > should_current:
            R = M - 1
        else:
            break
        if stop():
            return
    afterwatch(cpu, sc, should_current, lambda: stop)

def aware(cpu, sc, input_file, output_file):
    solar_currents = read_file(input_file)
    tex_plot(output_file, solar_currents, 'Solar Currents')
    solar_currents.reverse()
    pi_currents = []
    pi_freqs = []
    window = []
    search = Thread()
    stop_search = False
    while True:
        window.append(solar_currents.pop())
        pi_currents.append(pi_current(sc))
        pi_freqs.append(cpu.get_frequencies()[0])
        if len(window) == 5:
            if search.is_alive():
                stop_search = True
                search.join()
                stop_search = False
            search = Thread(
                        target=log_search,
                        args=(cpu, sc, statistics.mean(window), lambda: stop_search)
                     )
            search.start()
            window = []
        if not solar_currents:
            break
        sleep(1)
    tex_plot(output_file, pi_currents, 'Pi Currents')
    tex_plot(output_file, pi_freqs, 'Pi Frequencies')

sleep(5)
# suncontrol config
sc = sdl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
     )

cpu = cpuFreq()
cpu.reset()
sleep(5)
aware(cpu, sc, 'solar_currents', 'freqs_aware')
cpu.reset()
