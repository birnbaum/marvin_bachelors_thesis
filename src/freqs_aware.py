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

def log_part_search(cpu, sc, should_current, L, R):
    is_current = pi_current(sc)
    freqs = cpu.available_frequencies
    freq_index = freqs.index(cpu.get_frequencies()[0])
    if not (L[1] < should_current < R[1]):
        if is_current < should_current:
            L[0] = freq_index
            L[1] = is_current
            R[0] = len(freqs) - 1
        elif is_current > should_current:
            L[0] = 0
            R[0] = freq_index
            R[1] = is_current
        else:
            return L, R
    M = math.floor((L + R) / 2)
    cpu.set_max_frequencies(freqs[M])
    sleep(5)
    is_current = pi_current(sc)
    if is_current < should_current:
        L[0] = M + 1
        L[1] = is_current
    elif is_current > should_current:
        R[0]= M - 1
        R[1] = is_current
    return L, R

def aware(cpu, sc, input_file, output_file):
    solar_currents = read_file(input_file)
    #tex_plot(output_file, solar_currents, 'Solar Currents')
    solar_currents.reverse()
    pi_currents = []
    pi_freqs = []
    window = []
    L = (0, 0)
    R = (0, 0)
    while solar_currents:
        window.append(solar_currents.pop())
        pi_currents.append(pi_current(sc))
        pi_freqs.append(cpu.get_frequencies()[0])
        if len(window) == 5:
            L, R = log_part_search(cpu, sc, statistics.mean(window), L, R)
            window = []
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
