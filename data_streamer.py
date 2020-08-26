#!/usr/bin/env python

import nidaqmx as daq
import time
import warnings
import math
import pyfirmata

class streamer(object):
    """
    encapsulates the various ways to stream data.

    Holds the function that loops forever at a locked rate to stream data at
    a precise Hz
    """
    def __init__(self):
        """
        Doesn't really do anything right now
        """
        
        return

    def arduino_stream(self, callback, stream_rate=1000, usb_port='/dev/cu.usbserial-DA011ECL'):
        """
        Connects to the arduino at usb port usb_port, then streams at stream rate samples / second

        Calls callback 'callback' function with [data_L, data_R, current_time] each tick.
        Has inbuilt logic to delay to maintain stream_rate

        Blocking; blocks forever. Use quit() to get out. This sometimes errors as it exits

        Note: You have to flash firmata onto the arduino. I flashed the full version
        details: https://www.instructables.com/id/Arduino-Installing-Standard-Firmata/
        """
        period = 1.0/stream_rate

        try:
            board = pyfirmata.Arduino(usb_port)
            # board = pyfirmata.Arduino('/dev/ttyACM0')
            it = pyfirmata.util.Iterator(board)
            it.start()
        except:
            print("Arduino not connected at port", usb_port)

            quit()

        analog_input_L = board.get_pin('a:2:i')
        analog_input_R = board.get_pin('a:3:i')

        print("Waiting for Arduino to initialize")
        while analog_input_L.read() is None:
            continue
        print("Successfully connected to Arduino")

        t = time.perf_counter()

        while True:
            t += period

            l_signal, r_signal = analog_input_L.read(), analog_input_R.read()

            callback([l_signal, r_signal, time.perf_counter()])

            try:
                time.sleep(t-time.perf_counter())
            except:
                warnings.warn('System may not be able to handle such high frame rate, lower the desired frequency or simplify your callback function')
                continue

    def ni_stream(self, callback, daq_name, channels=["Dev1/ai0","Dev1/ai1"], stream_rate=1000):
        """
        Entirely untested! Pretty much straight copied from Ling's code

        I think that channels should take the form as seen above
        """
        daqtask = daq.Task(daq_name)

        for chn in channels:
            daqtask.ai_channels.add_ai_voltage_chan(chn)
        daqtask.timing.cfg_samp_clk_timing(stream_rate)

    def fake_stream(self, callback, stream_rate=1000):
        """
        Generates false data at rate (stream_rate / second)

        Blocking; blocks forever. Use quit() to get out. This sometimes errors as it exits.

        Calls callback 'callback' function with [data_L, data_R, current_time] each tick.
        Has inbuilt logic to delay to maintain stream_rate

        Edit this method to get simular or different signals
        """
        period = 1.0/stream_rate

        t = time.perf_counter()
        i = 0
        while True:
            t += period
            i += period

            raw_signal = abs(math.sin(4*i + math.pi/2))

            callback([raw_signal, raw_signal, time.perf_counter()])

            try:
                time.sleep(t-time.perf_counter())
            except:
                warnings.warn('System may not be able to handle such high frame rate, lower the desired frequency or simplify your callback fucntion')
                continue
