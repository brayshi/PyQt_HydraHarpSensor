from PyQt5.QtWidgets import QMessageBox
import numpy as np
import struct
from PyQt5.QtCore import QObject, pyqtSignal
from Trace import Trace
from Histogram import Histogram
from collections import deque


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
    trace_update = pyqtSignal()
    hist_update  = pyqtSignal()
    coarse_graph_update = pyqtSignal()
    coarse_graph_show = pyqtSignal()
    label_update = pyqtSignal()
    

    def __init__(self):
        super().__init__()
        self.inputFile = None # this returns the opened up version of the file
        self.trace = Trace()
        self.hist = Histogram(4*1e-12, 13333394)

        self.coarse_binning = None
        self.coarse_on = False
        self.coarse_ofl = 0
        self.coarse_indx = 0

        self._scaling_on = False

        self.ofl = 0
        self.seconds_ofl = 0
        self.buffer = deque(maxlen=MAX_BUFFER_SIZE)

        self.donor_counts = 0
        self.acceptor_counts = 0
        self.fret_counts = 0

        self.msgBox = QMessageBox()
        self.construct_msgBox()
    
    def change_trace_period(self, value):
        # if value is in range (0, 1], then set it to this value. Else keep it normal
        new_period = int(value)
        if new_period > self.trace.bin_size_milliseconds and new_period <= 1000:
            self.trace.period_milliseconds_next = new_period

    # called by QTimer in PyQt_Application every 1 ms. Tails inputfile and saves its contents into circular buffer
    def frameData(self):
        global message_window_on
        while self.inputFile:
            recordData = self.inputFile.read(256)
            if not recordData:
                break
            # split recordData into a list of 4 bytes in each element, since there's 4 bytes per 32 bit integer
            for i in range(0, len(recordData), 4):
                self.buffer.append(struct.unpack("<I", recordData[i:i+4])[0])

        # if len(buffer) is equal to the maximum buffer size, then pop up warning window
        if len(self.buffer) == MAX_BUFFER_SIZE and message_window_on == False:
            #ctypes.windll.user32.MessageBoxW(0, "WARNING_INPT_RATE_RATIO:\nThe pulse rate ratio R(ch)/R(sync) is over 5%\nfor at least one input channel.\nThis may cause pile-up and deadtime artifacts.", "WARNING", 0)
            self.msgBox.setVisible(True)
            message_window_on = True
        elif message_window_on == True and len(self.buffer) != MAX_BUFFER_SIZE:
            message_window_on = False
        
        if self.buffer:
            self.update()

    def construct_msgBox(self):
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setText("WARNING_INPT_RATE_RATIO:\nThe pulse rate ratio R(ch)/R(sync) is over 5%\nfor at least one input channel.\nThis may cause pile-up and deadtime artifacts.")
        self.msgBox.setWindowTitle("WARNING")
        self.msgBox.setStandardButtons(QMessageBox.Close)

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
                        if (self.coarse_binning and self.coarse_binning._coarse_finished == False):
                            self.coarse_ofl += 1
                    else:
                        self.ofl += nsync
                        if (self.coarse_binning and self.coarse_binning._coarse_finished == False):
                            self.coarse_ofl += nsync

                if (self.coarse_binning and self.coarse_ofl >= OVERFLOW_SECOND * self.coarse_binning._bin_size_seconds and self.coarse_binning._coarse_finished == False):
                    if (self.coarse_on == True):
                        max_value = max(self.coarse_binning.donor_line[self.coarse_indx], self.coarse_binning.acceptor_line[self.coarse_indx], self.coarse_binning.fret_line[self.coarse_indx])
                        if (self.coarse_binning._max_height * 1.2 <= max_value):
                            self.coarse_binning._max_height = max_value
                        self.coarse_graph_update.emit()
                    self.coarse_ofl = 0
                    self.coarse_indx += 1
                    if (self.coarse_indx > self.coarse_binning._seconds//self.coarse_binning._bin_size_seconds):
                        self.coarse_binning._coarse_finished = True
                
                if self.ofl >= trace_overflow * np.prod(self.trace.period.shape): # once the overflow amount is over a threshold,
                    # add the values into the graph's lists
                    # draw new trace frame
                    self.trace._prev_max_height = self.trace._max_height
                    if (self.coarse_on == False):
                        self.trace_update.emit()
                    self.hist_update.emit()

                    # reset the values, and finish the function call
                    self.seconds_ofl += self.ofl
                    self.ofl = 0

                    # if it's been a second since the donor counts were updated, update the labels
                    if (self.seconds_ofl >= OVERFLOW_SECOND):
                        self.label_update.emit()
                        self.seconds_ofl = 0
                        self.donor_counts = 0
                        self.acceptor_counts = 0
                        self.fret_counts = 0
                    
                    DA_start = self.trace._DA_range[0]
                    DA_end = self.trace._DA_range[1]
                    self.trace._fret_on = self.trace._fret_on_next
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
                hist_indx = int((dtime * self.hist.measDescRes * 1e12)//self.hist.bin_size_picoseconds)-2

                if channel == GREEN:
                    self.trace.green_line[trace_indx] += 1
                    self.hist.green_bins[hist_indx] += 1
                    self.donor_counts += 1
                    if (self.coarse_binning and self.coarse_binning._coarse_finished == False):
                        self.coarse_binning._donor_line[self.coarse_indx] += 1
                    if (self.trace.green_line[trace_indx] >= self.trace._max_height * 1.2):
                        self.trace._max_height = self.trace.green_line[trace_indx]
                elif channel == RED:
                    # if the dtime is between the green range in the histogram, add to the fret instead of the red
                    if DA_start <= dtime and dtime <= DA_end and (self.trace._fret_on == True or self.coarse_binning):
                        self.fret_counts += 1
                        if (self.trace._fret_on == True):
                            self.trace._fret_line[trace_indx] += 1
                        else:
                            self.trace.red_line[trace_indx] += 1
                        if (self.coarse_binning and self.coarse_binning._coarse_finished == False):
                            self.coarse_binning.fret_line[self.coarse_indx] += 1
                        if (self.trace.red_line[trace_indx] >= self.trace._max_height * 1.2):
                            self.trace._max_height = self.trace.red_line[trace_indx]
                    else:
                        self.acceptor_counts += 1
                        self.trace.red_line[trace_indx] += 1
                        if (self.coarse_binning and self.coarse_binning._coarse_finished == False):
                            self.coarse_binning._acceptor_line[self.coarse_indx] += 1
                        if (self.trace.red_line[trace_indx] >= self.trace._max_height * 1.2):
                            self.trace._max_height = self.trace.red_line[trace_indx]
                    self.hist.red_bins[hist_indx] += 1
