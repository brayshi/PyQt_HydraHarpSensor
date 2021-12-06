import numpy as np

# the amount of overflows needed for a 1 ms overflow update
OVERFLOW_MILLISECOND = 13
HIST_BIN_AMOUNT = 2**15-1
CONVERT_SECONDS = 1000

class CoarseBinning:
    @property
    def bin_size_milliseconds(self):
        return self._bin_size_milliseconds

    @bin_size_milliseconds.setter
    def bin_size_milliseconds(self, value):
        self._bin_size_milliseconds = value

    @property
    def bin_size_milliseconds_next(self):
        return self._bin_size_milliseconds_next

    @bin_size_milliseconds_next.setter
    def bin_size_milliseconds_next(self, value):
        self._bin_size_milliseconds_next = value
    
    @property
    def period_milliseconds(self):
        return self._period_milliseconds
    
    @period_milliseconds.setter
    def period_milliseconds(self, value):
        self._period_milliseconds = value

    @property
    def period_milliseconds_next(self):
        return self._period_milliseconds_next

    @period_milliseconds_next.setter
    def period_milliseconds_next(self, value):
        self._period_milliseconds_next = value
    
    @property
    def period(self):
        return self._period

    @property
    def green_line(self):
        return self._green_line

    @green_line.setter
    def green_line(self, indx):
        if (self._bin_size_milliseconds >= 100):
            self._green_line = np.roll(self._green_line, -1) # remove oldest value
            self._green_line[np.prod(self._period.size)-1] += 1
        else:
            self._green_line[indx] += 1
    
    @property
    def red_line(self):
        return self._red_line
    
    @red_line.setter
    def red_line(self, indx):
        if (self._bin_size_milliseconds >= 100):
            self._red_line = np.roll(self._red_line, -1) # remove oldest value
            self._red_line[np.prod(self._period.size)-1] += 1
        else:
            self._red_line[indx] += 1

    @property
    def fret_line(self):
        return self._fret_line
    
    @fret_line.setter
    def fret_line(self, indx):
        if (self._bin_size_milliseconds >= 100):
            self._fret_line = np.roll(self._fret_line, -1) # remove oldest value
            self._fret_line[np.prod(self._period.size)-1] += 1
        else:
            self._fret_line[indx] += 1

    def __init__(self, seconds):
        super().__init__()
        self._seconds = seconds
        self._period = np.arange(0, seconds, step=1)
        self._green_line = np.zeros(seconds, dtype=np.uint32, order='C')
        self._red_line = np.zeros(seconds, dtype=np.uint32, order='C')
        self._fret_line = np.zeros(seconds, dtype=np.uint32, order='C')