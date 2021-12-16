import numpy as np

# the amount of overflows needed for a 1 ms overflow update
OVERFLOW_MILLISECOND = 13
HIST_BIN_AMOUNT = 2**15-1
CONVERT_SECONDS = 1000

class CoarseBinning:
    @property
    def bin_size_seconds(self):
        return self._bin_size_milliseconds

    @bin_size_seconds.setter
    def bin_size_milliseconds(self, value):
        self._bin_size_milliseconds = value

    @property
    def bin_size_seconds_next(self):
        return self._bin_size_milliseconds_next

    @bin_size_seconds_next.setter
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
    def donor_line(self):
        return self._donor_line

    @donor_line.setter
    def donor_line(self, indx):
        if (self._bin_size_milliseconds >= 100):
            self._donor_line = np.roll(self._donor_line, -1) # remove oldest value
            self._donor_line[np.prod(self._period.size)-1] += 1
        else:
            self._donor_line[indx] += 1
    
    @property
    def acceptor_line(self):
        return self._acceptor_line
    
    @acceptor_line.setter
    def acceptor_line(self, indx):
        if (self._bin_size_milliseconds >= 100):
            self._acceptor_line = np.roll(self._acceptor_line, -1) # remove oldest value
            self._acceptor_line[np.prod(self._period.size)-1] += 1
        else:
            self._acceptor_line[indx] += 1

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

    def __init__(self, seconds, bin_size_seconds):
        super().__init__()
        self._seconds = seconds
        self._bin_size_seconds = bin_size_seconds
        self._max_height = 0
        self._coarse_finished = False
        self._period = np.arange(0, seconds + self._bin_size_seconds, step=self._bin_size_seconds)
        self._donor_line = np.zeros(int(self._seconds//self._bin_size_seconds)+1, dtype=np.uint32, order='C')
        self._acceptor_line = np.zeros(int(self._seconds//self._bin_size_seconds)+1, dtype=np.uint32, order='C')
        self._fret_line = np.zeros(int(self._seconds//self._bin_size_seconds)+1, dtype=np.uint32, order='C')