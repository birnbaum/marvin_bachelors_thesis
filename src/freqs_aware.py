#!/usr/bin/env python3

from time import sleep
from statistics import mean
from math import floor
from threading import Thread
from cpufreq import cpuFreq
from lib import SDL_Pi_SunControl as sdl

cpu = cpuFreq()
# suncontrol config
sc = sdl.SDL_Pi_SunControl(
        INA3221Address = 0x40,
        USBControlEnable = 26,
        USBControlControl = 21,
        WatchDog_Done = 13,
        WatchDog_Wake = 16
     )

def read_file(file_name):
    with open(file_name) as file:
        return [int(float(line.rstrip())) * 3 for line in file]

def tex_plot(output_file, data, legendentry):
    with open(output_file, 'a') as file:
        file.write('\\addplot\ncoordinates {\n')
        for cputime, current in enumerate(data):
            file.write(f'({cputime + 1},{current})\n')
        file.write(f'}};\n\\addlegendentry{{{legendentry}}}\n')

def pi_current():
    return int(sc.readChannelCurrentmA(sdl.SunControl_OUTPUT_CHANNEL))

class Bound:
    def __init__(self, index = 0, current = 0):
        self.index = index
        self.current = current

def log_search_step(current_should, L, R, last_modified):
    current_is = pi_current()
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
        last_modified = None
    # If current_should is now between current_is and
    # Bound.current of the last is_mod bound, there is
    # no frequency inbetween and the lower frequency of
    # of the two is chosen
    if L == last_modified:
        if L.current <= current_should <= current_is:
            # frequency of the left bound is currently higher
            cpu.set_max_frequencies(freqs[L.index - 1])
            sleep(5)
            return L, R, last_modified
        else:
            last_modified = None
    if R == last_modified:
        if current_is <= current_should <= R.current:
            # frequency is already the lower one of the two
            return L, R, last_modified
        else:
            last_modified = None
    M = floor((L.index + R.index) / 2)
    cpu.set_max_frequencies(freqs[M])
    sleep(5)
    current_is = pi_current()
    # ignore half the search interval:
    # Because the index of the bound is M +- 1 and not M,
    # current_is is not the actual current to the frequency,
    # and therefore last_modified = Bound.
    if current_is < current_should:
        new_index = M + 1 if M < len(freqs) - 1 else M
        L = Bound(new_index, current_is)
        last_modified = L
    elif current_is > current_should:
        new_index = M - 1 if M > 0 else M
        R = Bound(new_index, current_is)
        last_modified = R
    return L, R, last_modified

def aware(input_file, output_file):
    solar_currents = read_file(input_file)
    #tex_plot(output_file, solar_currents, 'Solar Currents')
    pi_currents = []
    pi_freqs = []
    window = []
    L = Bound()
    R = Bound()
    last_modified = None
    search = Thread()
    while solar_currents:
        pi_currents.append(pi_current())
        pi_freqs.append(cpu.get_frequencies()[0])
        if len(window) > 4:
            window.pop(0)
        window.append(solar_currents.pop(0))
        if not search.is_alive() and len(window) == 5:
            search = Thread(
                        target=log_search_step,
                        args=(mean(window), L, R, last_modified)
                     )
            search.start()
            window = []
        sleep(1)
    tex_plot(output_file, pi_currents, 'Pi Currents')
    tex_plot(output_file, pi_freqs, 'Pi Frequencies')

cpu.reset()
sleep(5)
aware('solar_currents', 'freqs_aware')
cpu.reset()
