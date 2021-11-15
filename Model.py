import ReadFile
import numpy as np
import struct
from PyQt5.QtCore import QObject, pyqtSignal
from Trace import Trace
from Histogram import Histogram
from collections import deque
import ctypes

# channel numbers
GREEN = 2
RED = 1

MAX_BUFFER_SIZE = 100096
BUFFER_READ = 256
OVERFLOW_SECOND = 13000
CONVERT_SECONDS = 1000

message_window_on = False

# Holds the inputfile and its necessary values, the trace, and the histogram. 
# Has a loop that automatically reads the header file so the controller doesn't have to do this
# Every time the overflow is exceeded, emits a signal to the controller that this has happened. The controller then tells the view to update
# Controller can also notify the model to change. This will be sent to the trace and histogram classes to be worked on
class Model(QObject):
    graph_update = pyqtSignal()

    def __init__(self, sys_argv):
        super().__init__()
        self.inputFile = ReadFile.confirmHeader(sys_argv) # this returns the opened up version of the file
        self.measDescRes = ReadFile.readHeader(self.inputFile) # this reads the inputfile and gives a measDescRes while also reading up to EOF
        self.trace = Trace()
        self.hist = Histogram(self.measDescRes)
        self.ofl = 0
        self.buffer = deque(maxlen=MAX_BUFFER_SIZE)

    def change_trace_bin_size(self, value):
        if value == 0:
            # this is 1 ms
            self.trace.bin_size_milliseconds_next = 1
        elif value == 1:
            # this is 10 ms
            self.trace.bin_size_milliseconds_next = 10
        elif value == 2:
            # this is 100 ms
            self.trace.bin_size_milliseconds_next = 100

    
    def change_trace_period(self, value):
        # if value is in range (0, 1], then set it to this value. Else keep it normal
        new_period = int(value)
        if new_period > self.trace.bin_size_milliseconds and new_period <= 1000:
            self.trace.period_milliseconds_next = new_period
    
    def change_hist_bin_size(self, value):
        if value == 0:
            # this is 64 ps
            self.hist.bin_size_picoseconds_next = 64
        elif value == 1:
            # this is 128 ps
            self.hist.bin_size_picoseconds_next = 128
        elif value == 2:
            # this is 256 ps
            self.hist.bin_size_picoseconds_next = 256

    # called by QTimer in PyQt_Application every 1 ms. Tails inputfile and saves its contents into circular buffer
    def frameData(self):
        global message_window_on
        while True:
            recordData = self.inputFile.read(256)
            if not recordData:
                break
            # split recordData into a list of 4 bytes in each element, since there's 4 bytes per 32 bit integer
            for i in range(0, len(recordData), 4):
                self.buffer.append(struct.unpack("<I", recordData[i:i+4])[0])

        # if len(buffer) is equal to the maximum buffer size, then pop up warning window
        if len(self.buffer) == MAX_BUFFER_SIZE and message_window_on == False:
            ctypes.windll.user32.MessageBoxW(0, "WARNING_INPT_RATE_RATIO:\nThe pulse rate ratio R(ch)/R(sync) is over 5%\nfor at least one input channel.\nThis may cause pile-up and deadtime artifacts.", "WARNING", 0)
            message_window_on = True
        elif len(self.buffer) != MAX_BUFFER_SIZE and message_window_on == True:
            message_window_on = False
        
        if self.buffer:
            self.update()

    # Called after frameData gets to End-of-File (EOF). Processes 4-byte integers using bitwise operations.
    # Reads both overflows and photon channel signals. When a specific amount of overflows is obtained in total,
    # emit a signal for the view to update its contents
    def update(self):
        # the start and end ranges for the fret signals. Only updates between view changes
        DA_start = self.trace._DA_range[0]
        DA_end = self.trace._DA_range[1]

        while self.buffer:
            # reads buffer value and does bitwise operations to find the necessary values
            recordData = self.buffer.popleft()
            special = recordData >> 31
            channel = (recordData >> 25) & 63
            dtime = (recordData >> 10) & 32767
            nsync = recordData & 1023

            # the amount of overflows per bin
            trace_overflow = OVERFLOW_SECOND * self.trace.bin_size_milliseconds / CONVERT_SECONDS
            if special == 1:
                if channel == 0x3F: # Overflow
                    # Number of overflows in nsync. If 0, it's an
                    # old style single overflow
                    if nsync == 0:
                        self.ofl += 1
                    else:
                        self.ofl += nsync
                if self.ofl >= trace_overflow * np.prod(self.trace.period.shape): # once the overflow amount is over a threshold,
                    # add the values into the graph's lists
                    # draw new trace frame
                    self.graph_update.emit()

                    # reset the values, and finish the function call
                    self.ofl = 0
                    DA_start = self.trace._DA_range[0]
                    DA_end = self.trace._DA_range[1]

                    self.trace.period_milliseconds = self.trace.period_milliseconds_next
                    self.trace.bin_size_milliseconds = self.trace.bin_size_milliseconds_next
                    if self.trace.bin_size_milliseconds > self.trace.period_milliseconds:
                        self.trace.period_milliseconds = self.trace.bin_size_milliseconds
                    self.trace.change_traces()

                    if (self.hist.bin_size_picoseconds != self.hist.bin_size_picoseconds_next):
                        self.hist.bin_size_picoseconds = self.hist.bin_size_picoseconds_next
                        self.hist.change_hist()

            else: # regular input channel
                # calculate indexes that the photons should be placed into
                trace_indx = int(self.ofl // trace_overflow)
                hist_indx = int((dtime * self.hist.measDescRes * 1e12)//self.hist.bin_size_picoseconds)-1

                if int(channel) == GREEN:
                    self.trace.green_line[trace_indx] += 1
                    self.hist.green_bins[hist_indx] += 1
                elif int(channel) == RED:
                    # if the dtime is between the green range in the histogram, add to the fret instead of the red
                    if DA_start <= dtime and dtime <= DA_end and self.trace._fret_on == True:
                        self.trace._fret_line[trace_indx] += 1
                    else:
                        self.trace.red_line[trace_indx] += 1
                    self.hist.red_bins[hist_indx] += 1
