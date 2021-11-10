from PyQt5.QtCore import pyqtSignal
import numpy as np

# the amount of overflows needed for a 1 ms overflow update
OVERFLOW_MILLISECOND = 13
HIST_BIN_AMOUNT = 2**15-1
CONVERT_SECONDS = 1000

class Histogram:
    bin_size_changed = pyqtSignal(int)
    height_changed = pyqtSignal(int)
    green_bins_change = pyqtSignal(int)
    red_bins_change = pyqtSignal(int)

    @property
    def height(self):
        return self._height
    
    @height.setter
    def height(self, value):
        self._height = value
        self.height_changed.emit(value)

    @property
    def bin_size_picoseconds(self):
        return self._bin_size_picoseconds

    @bin_size_picoseconds.setter
    def bin_size_picoseconds(self, value):
        self._bin_size_picoseconds = value

    @property
    def bin_size_picoseconds_next(self):
        return self._bin_size_picoseconds_next

    @bin_size_picoseconds_next.setter
    def bin_size_picoseconds_next(self, value):
        self._bin_size_picoseconds_next = value

    @property
    def measDescRes(self):
        return self._measDescRes

    @property
    def green_bins(self):
        return self._green_bins

    @green_bins.setter
    def green_bins(self, indx):
        self._green_bins[indx] += 1
        self.green_bins_change.emit()

    @property
    def red_bins(self):
        return self._red_bins

    @red_bins.setter
    def red_bins(self, indx):
        self._red_bins[indx] += 1
        self.red_bins_change.emit()

    def change_hist(self):
        binMultiple = int(-(self.bin_size_picoseconds // -(self.measDescRes * 1e12)))
        num_bins = int(-(HIST_BIN_AMOUNT // -binMultiple))
        self._period = np.linspace(0, HIST_BIN_AMOUNT * self.measDescRes * 1e9, num=num_bins, endpoint=True)
        self._green_bins = np.zeros(num_bins, dtype=np.uint32, order='C')
        self._red_bins = np.zeros(num_bins, dtype=np.uint32, order='C')

    def __init__(self, measDescRes):
        self._height = 5 # this is the exponent for height in logs (ex: 10^self._height)
        self._period_picoseconds = 100000 # will convert this to nanoseconds for period
        self._bin_size_picoseconds = 64 # can only be 16, 64, and 256
        self._bin_size_picoseconds_next = 64 # the next value for bin size that will be applied later
        self._measDescRes = measDescRes
        binMultiple = int(-(self.bin_size_picoseconds // -(self.measDescRes * 1e12)))
        num_bins = int(-(HIST_BIN_AMOUNT // -binMultiple))
        self._period = np.linspace(0, HIST_BIN_AMOUNT * self._measDescRes * 1e9, num=num_bins, endpoint=True)
        self._green_bins = np.zeros(num_bins, dtype=np.uint32, order='C')
        self._red_bins = np.zeros(num_bins, dtype=np.uint32, order='C')

        # for fret signals (if red is in green range, then consider it a fret)
        self._green_range = np.array([0.0, 75.0])
        self._red_range = np.array([0.0, 75.0])