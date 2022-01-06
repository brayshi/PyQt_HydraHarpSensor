from PyQt5 import uic
from PyQt5.QtGui import QColor, QIntValidator
from PyQt5.QtWidgets import QFileDialog, QMainWindow
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from pyqtgraph.functions import mkPen
import ReadFile
from CoarseBinning import CoarseBinning

class View(QMainWindow):
    def __init__(self, model):
        super(View, self).__init__()
        uic.loadUi('appwindow.ui', self)
        self.show()
        self.win = QtGui.QWidget()

        self._model = model

        self.create_view()

    def create_view(self):

        # Trace Widget with green_line and red_line, with a set Y Range
        self.trace.setMouseEnabled(x=False, y=False)
        self.donor_trace = self.trace.plot(self._model.trace.period, self._model.trace.green_line, pen='g')
        self.acceptor_trace = self.trace.plot(self._model.trace.period, self._model.trace.red_line, pen='r')
        self.fret_trace = self.trace.plot(self._model.trace.period, self._model.trace.fret_line, pen=mkPen(QColor(85, 85, 255)))
        self.trace.setYRange(0, 100, padding=0)
        self.trace.setLabels(title='Trace Graph', left='photons per ' + str(self._model.trace._bin_size_milliseconds) + ' ms bin', bottom='time (ms)')

        # Histogram Widget with green_hist and red_hist, with a set Y Range
        self.hist.setMouseEnabled(x=False, y=False)
        self.donor_hist = self.hist.plot(self._model.hist._period, self._model.hist._green_bins, pen='g')
        self.acceptor_hist = self.hist.plot(self._model.hist._period, self._model.hist._red_bins, pen='r')
        self.hist.getPlotItem().setLogMode(x=None, y=True)
        self.hist.setYRange(0, 5, padding=0)
        self.hist.setXRange(0, 75, padding=0)
        self.hist.setLabels(title='Histogram', left='photons per ' + str(self._model.hist._bin_size_picoseconds) + ' ps bin', bottom='time (ns)')

        # lines that can be moved to set DA and DD ranges
        self.donor_start = pg.InfiniteLine(pos=5, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='y', label="d_start", name="green_start")
        self.donor_start.label.setPosition(0.95)
        self.donor_end = pg.InfiniteLine(pos=35, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='y', label="d_end", name="green_end")
        self.donor_end.label.setPosition(0.95)
        self.acceptor_start = pg.InfiniteLine(pos=40, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='y', label="a_start", name="red_start")
        self.acceptor_start.label.setPosition(0.90)
        self.acceptor_end = pg.InfiniteLine(pos=65, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='y', label="a_end", name="red_end")
        self.acceptor_end.label.setPosition(0.90)

        self.hist.addItem(self.donor_start)
        self.hist.addItem(self.donor_end)
        self.hist.addItem(self.acceptor_start)
        self.hist.addItem(self.acceptor_end)

        self.donor_start.label.setColor(QColor(0, 255, 0))
        self.donor_end.label.setColor(QColor(0, 255, 0))
        self.acceptor_start.label.setColor(QColor(255, 0, 0))
        self.acceptor_end.label.setColor(QColor(255, 0, 0))

        # signals when the green lines have changed
        self.donor_start.sigPositionChangeFinished.connect(self.DA_start)
        self.donor_end.sigPositionChangeFinished.connect(self.DA_end)

        # Trace Period QSpinBox that changes when returnPressed(). Should be a float and have 'ms' present (basically, 1000 ms would be the default value and can't go above. SI unit stays)
        self.tracePeriodLine.setText("1000")
        self.tracePeriodLine.setValidator(QIntValidator(self))
        self.tracePeriodLine.editingFinished.connect(self.change_trace_period)

        # Combo Box for ms Bins should be an int and have 'ms' present
        self.traceBinLine.setText("1")
        self.traceBinLine.setValidator(QIntValidator(self))
        self.traceBinLine.editingFinished.connect(self.change_trace_bin_size)

        # Combo Box for ps Bins should be an int and have 'ps' present
        self.histBinLine.setText("64")
        self.histBinLine.editingFinished.connect(self.change_hist_bin_size)

        # Trace Axis Height (cast to int)
        self.traceAxisLine.setText("100")
        self.traceAxisLine.setValidator(QIntValidator(10, 100000, self))
        self.traceAxisLine.editingFinished.connect(self.change_trace_height)

        self.syncRateLine.setText("13333394")

        # Histogram Axis Height (cast to int)
        self.histAxisLine.setText("5")
        self.histAxisLine.setValidator(QIntValidator(1, 10, self))
        self.histAxisLine.editingFinished.connect(self.change_hist_height)

        self.fretButton.clicked.connect(self.change_fret_on)

        self.coarseTraceLine.setText("1800")
        self.coarseTraceLine.setValidator(QIntValidator(1, 7200, self))

        self.coarseTraceButton.clicked.connect(self.change_trace_graph)

        self.fileButton.clicked.connect(self.change_file)

        self.resetCoarseButton.clicked.connect(self.reset_coarse_graph)

        self.coarseScaleButton.clicked.connect(self.scale_graph)

        self.resetHistButton.clicked.connect(self.reset_hist)

        self.donorColourBox.addItems(["Violet (405 nm)", "Blue (446 nm)", "Cyan (477 nm)", "Teal (518 nm)", "Green (545 nm)", "Red (637 nm)"])
        self.donorColourBox.activated.connect(self.change_donor_colour)
        self.donorColourBox.setCurrentIndex(4)
        self.acceptorColourBox.addItems(["Violet (405 nm)", "Blue (446 nm)", "Cyan (477 nm)", "Teal (518 nm)", "Green (545 nm)", "Red (637 nm)"])
        self.acceptorColourBox.activated.connect(self.change_acceptor_colour)
        self.acceptorColourBox.setCurrentIndex(5)
        self.fretColourBox.addItems(["Blue", "Yellow"])
        self.fretColourBox.activated.connect(self.change_fret_colour)

        self.coarseBinLine.setText("1")
        self.coarseBinLine.setValidator(QIntValidator(parent=self))
        self.coarseBinLine.editingFinished.connect(self.change_coarse_bin_size)

        

    # change file being tailed by model
    def change_file(self):
        file = QFileDialog.getOpenFileName(self, "Open PTU file", "This PC", "PTU files (*.ptu)")
        self._model.inputFile = ReadFile.confirmHeader(file)
        self.reset_hist()
        self.reset_coarse_graph()
        self.fileButton.setText("...")

    # if button is pressed, fret signal will be toggled on/off
    def change_fret_on(self):
        if self._model.trace._fret_on_next == True:
            self._model.trace._fret_on_next = False
            self.fretButton.setText("OFF")
        else:
            self._model.trace._fret_on_next = True
            self.fretButton.setText("ON")

    def change_trace_graph(self):
        if self._model.coarse_on == False:
            if int(self.coarseTraceLine.text()) > 0 and self._model.coarse_binning == None:
                self._model.coarse_binning = CoarseBinning(int(self.coarseTraceLine.text()), int(self.coarseBinLine.text()))
            self._model.coarse_on = True
            self.coarseTraceButton.setText("ON (running)")
            self.trace.setLabels(title='Coarse Trace Graph', left='photons per ' + str(self._model.coarse_binning._bin_size_seconds) + ' s bin', bottom='time (s)')
            self._model.coarse_graph_show.emit()
            self.trace.setXRange(0, self._model.coarse_binning._seconds, padding=0)
        elif self._model.coarse_on == True:
            self._model.coarse_on = False
            self.coarseTraceButton.setText("OFF (running)")
            self.trace.setLabels(title='Trace Graph', left='photons per ' + str(self._model.trace._bin_size_milliseconds) + ' ms bin', bottom='time (ms)')
            self._model.trace_update.emit()
            self.trace.setXRange(0, int(self.tracePeriodLine.text())/1000, padding=0)

    def reset_coarse_graph(self):
        self._model.coarse_binning = None
        self.coarseTraceButton.setText("OFF")
        self._model.coarse_on = False
        self._model.coarse_indx = 0
        self._model.coarse_ofl = 0
        self.trace.setLabels(title='Trace Graph', left='photons per ' + str(self._model.trace._bin_size_milliseconds) + ' ms bin', bottom='time (ms)')
        self._model.trace_update.emit()
        self.trace.setXRange(0, int(self.tracePeriodLine.text())/1000, padding=0)
        if (self._model._scaling_on == True):
            self.trace.setYRange(0, self._model.trace._max_height*1.2, padding=0)
        else:
            self.trace.setYRange(0, int(self.traceAxisLine.text()), padding=0)

    def change_donor_colour(self, value):
        colour = self.choose_colour(value)
        self.donor_trace.setPen(colour[0])
        self.donor_hist.setPen(colour[0])
        self.donorCountsLabel_1.setStyleSheet(colour[1])
        self.donorCountsLabel_2.setStyleSheet(colour[1])
        self.donor_start.setPen(colour[0])
        self.donor_end.setPen(colour[0])
        self.donor_start.label.setColor(colour[0])
        self.donor_end.label.setColor(colour[0])

    def choose_colour(self, value):
        # this is violet
        if (value == 0):
            colour = (QColor(170, 0, 255), 'color: rgb(170, 0, 255)')
        # this is blue
        elif (value == 1):
            colour = (QColor(4, 51, 255), 'color: rgb(4, 51, 255)')
        # this is Cyan
        elif (value == 2):
            colour = (QColor(118, 214, 255), 'color: rgb(118, 214, 255)')
        # this is Teal
        elif (value == 3):
            colour = (QColor(0, 145, 147), 'color: rgb(0, 145, 147)')
        # this is Green
        elif (value == 4):
            colour = (QColor(0, 255, 0), 'color: rgb(0, 255, 0)')
        # this is Red
        else:
            colour = (QColor(255, 0, 0), 'color: rgb(255, 0, 0)')
        return colour

    def change_acceptor_colour(self, value):
        colour = self.choose_colour(value)
        self.acceptor_trace.setPen(colour[0])
        self.acceptor_hist.setPen(colour[0])
        self.acceptorCountsLabel_1.setStyleSheet(colour[1])
        self.acceptorCountsLabel_2.setStyleSheet(colour[1])
        self.acceptor_start.setPen(colour[0])
        self.acceptor_end.setPen(colour[0])
        self.acceptor_start.label.setColor(colour[0])
        self.acceptor_end.label.setColor(colour[0])


    def change_fret_colour(self, value):
        if value == 0:
            colour = (QColor(85, 85, 255), 'color: rgb(85, 85, 255)')
        else:
            colour = ('y', 'color: yellow')
        self.fret_trace.setPen(colour[0])
        self.fretCountsLabel_1.setStyleSheet(colour[1])
        self.fretCountsLabel_2.setStyleSheet(colour[1])

    def change_trace_bin_size(self):
        value = int(self.traceBinLine.text())
        if (value < 1):
            self.traceBinLine.setText("1")
            value = 1
        elif (value > 999):
            self.traceBinLine.setText("999")
            value = 999
        self._model.trace.bin_size_milliseconds_next = value

    def change_coarse_bin_size(self):
        if (int(self.coarseBinLine.text()) < 1):
            self.coarseBinLine.setText("1")
        elif (int(self.coarseBinLine.text()) > 10):
            self.coarseBinLine.setText("10")

    def change_hist_bin_size(self):
        value = int(self.histBinLine.text())
        if (value < self._model.hist.measDescRes * 1e12):
            value =int(self._model.hist.measDescRes * 1e12)
            self.histBinLine.setText(str(value))
        elif (value > 4096):
            self.histBinLine.setText("4096")
            value = 4096
        self._model.hist.bin_size_picoseconds_next = value
    
    def scale_graph(self):
        if (self._model._scaling_on == True):
            self._model._scaling_on = False
            self.coarseScaleButton.setText("OFF")
            self.trace.setYRange(0, int(self.traceAxisLine.text()), padding=0)
        elif (self._model._scaling_on == False):
            self._model._scaling_on = True
            self.coarseScaleButton.setText("ON")
            if (self._model.coarse_on == True):
                self.trace.setYRange(0, self._model.coarse_binning._max_height*1.2, padding=0)
            else:
                self.trace.setYRange(0, self._model.trace._max_height*1.2, padding=0)
                
    def reset_hist(self):
        tuple_val = ReadFile.readHeader(self._model.inputFile)
        self._model.hist._measDescRes = tuple_val[0]
        # route #1: use the syncRate read from the header
        if (tuple_val[1] != None and tuple_val[1] != 0):
            self._model.hist._syncRate = tuple_val[1]
            self.syncRateLine.setText(str(tuple_val[1]))
        # if this doesn't work, read the text from the sync Rate box
        else:
            self._model.hist._syncRate = int(self.syncRateLine.text())
            print("had to read from the sync rate line edit")
        self._model.hist.change_hist()
        self.histBinLine.setText(str(self._model.hist.bin_size_picoseconds))
        self.hist.setLabels(title='Histogram', left='photons per ' + str(self._model.hist._bin_size_picoseconds) + ' ps bin', bottom='time (ns)')

    # change trace period that will be displayed for the next frame
    def change_trace_period(self):
        value = int(self.tracePeriodLine.text())
        if (value < self._model.trace.bin_size_milliseconds_next):
            self.tracePeriodLine.setText(str(self._model.trace.bin_size_milliseconds_next))
            value = int(self._model.trace.bin_size_milliseconds_next)
        elif (value > 2000):
            self.tracePeriodLine.setText("2000")
            value = 2000
        self._model.trace._period_milliseconds_next = value
    
    # change trace graph's height
    def change_trace_height(self):
        if (self._model._scaling_on == False):
            self.trace.setYRange(0, int(self.traceAxisLine.text()), padding=0)
    
    # change histogram's height
    def change_hist_height(self):
        self.hist.setYRange(0, int(self.histAxisLine.text()), padding=0)

    # changes where the DA signal starts for calculating fret
    def DA_start(self):
        self._model.trace._DA_range[0] = (self.donor_start.value()*1e-9)/self._model.hist._measDescRes
    
    # changes where the DA signal ends for calculating fret
    def DA_end(self):
        self._model.trace._DA_range[1] = (self.donor_end.value()*1e-9)/self._model.hist._measDescRes