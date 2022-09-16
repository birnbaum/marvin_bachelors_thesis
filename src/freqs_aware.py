#!/usr/bin/env python3

from time import sleep
import statistics
import math
#from threading import Thread
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

class Bound:
    def __init__(self, index = 0, current = 0, is_actual = True):
        self.index = index
        self.current = current
        self.is_actual = is_actual

def log_search_step(cpu, sc, current_should, L, R):
    current_is = pi_current(sc)
    freqs = cpu.available_frequencies
    freq_index = freqs.index(cpu.get_frequencies()[0])
    # current_should can change at any time, therefore if
    # outside of search interval, restart the search.
    if not (L.current <= current_should <= R.current):
        if current_is < current_should:
            L = Bound(freq_index, current_is)
            R = Bound(len(freqs) - 1, 0)
        elif current_is > current_should:
            R = Bound(freq_index, current_is)
            L = Bound()
    # If current_should is now between current_is and
    # Bound.current of the last altered bound, there is
    # no frequency inbetween and the lower frequency of
    # of the two is chosen
    if not L.is_actual:
        if L.current <= current_should <= current_is:
            # frequency of the left bound is currently higher
            cpu.set_max_frequencies(freqs[L.index - 1])
            sleep(5)
            return L, R
        else:
            L.is_actual = True
    if not R.is_actual:
        if current_is <= current_should <= R.current:
            # frequency is already the lower one of the two
            return L, R
        else:
            R.is_actual = True
    M = math.floor((L.index + R.index) / 2)
    cpu.set_max_frequencies(freqs[M])
    sleep(5)
    current_is = pi_current(sc)
    # ignore half the search interval:
    # Because the index of the bound is M +- 1 and not M,
    # current_is is not the actual current to the frequency,
    # and therefore is_actual = False.
    if current_is < current_should:
        new_index = M + 1 if M < len(freqs) - 1 else M
        L = Bound(new_index, current_is, False)
    elif current_is > current_should:
        new_index = M - 1 if M > 0 else M
        R = Bound(new_index, current_is, False)
    return L, R

def aware(cpu, sc, input_file, output_file):
    solar_currents = read_file(input_file)
    #tex_plot(output_file, solar_currents, 'Solar Currents')
    solar_currents.reverse()
    pi_currents = []
    pi_freqs = []
    window = []
    L = Bound()
    R = Bound()
    while solar_currents:
        window.append(solar_currents.pop())
        pi_currents.append(pi_current(sc))
        pi_freqs.append(cpu.get_frequencies()[0])
        if len(window) == 5:
            L, R = log_search_step(cpu, sc, statistics.mean(window), L, R)
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
