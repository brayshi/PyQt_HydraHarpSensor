from PyQt5 import uic
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QMainWindow, QComboBox
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
from Widgets import TextBox

class View(QMainWindow):
    def __init__(self, model):
        super(View, self).__init__()
        uic.loadUi('appwindow.ui', self)
        self._model = model

        self.win = QtGui.QWidget()

        # Trace Widget with green_line and red_line, with a set Y Range
        self.green_trace = self.trace.plot(self._model.trace.period, self._model.trace.green_line, pen='g')
        self.red_trace = self.trace.plot(self._model.trace.period, self._model.trace.red_line, pen='r')
        self.fret_trace = self.trace.plot(self._model.trace.period, self._model.trace.fret_line, pen='b')
        self.trace.setYRange(0, self._model.trace.height, padding=0.005)

        # Histogram Widget with green_hist and red_hist, with a set Y Range
        self.green_hist = self.hist.plot(self._model.hist._period, self._model.hist._green_bins, pen='g')
        self.red_hist = self.hist.plot(self._model.hist._period, self._model.hist._red_bins, pen='r')
        self.hist.getPlotItem().setLogMode(x=None, y=True)
        self.hist.setYRange(0, 5, padding=0.01)
        self.hist.setXRange(0, 75, padding=0)

        # lines that can be moved to set DA and DD ranges
        self.green_start = pg.InfiniteLine(pos=5, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="g_start", name="green_start")
        self.green_end = pg.InfiniteLine(pos=35, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="g_end", name="green_end")
        self.red_start = pg.InfiniteLine(pos=40, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="r_start", name="red_start")
        self.red_end = pg.InfiniteLine(pos=65, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="r_end", name="red_end")

        self.hist.addItem(self.green_start)
        self.hist.addItem(self.green_end)
        self.hist.addItem(self.red_start)
        self.hist.addItem(self.red_end)

        # signals when the green lines have changed
        self.green_start.sigPositionChangeFinished.connect(self.DA_start)
        self.green_end.sigPositionChangeFinished.connect(self.DA_end)

        # Trace Period QSpinBox that changes when returnPressed(). Should be a float and have 'ms' present (basically, 1000 ms would be the default value and can't go above. SI unit stays)
        self.tracePeriodLine.setText("1000")
        self.tracePeriodLine.setValidator(QIntValidator(1, 1000, self))
        self.tracePeriodLine.editingFinished.connect(self.change_trace_period)

        # Combo Box for ms Bins should be an int and have 'ms' present
        self.traceBinCombo.addItems(["1 ms", "10 ms", "100 ms"])
        self.traceBinCombo.activated.connect(self._model.change_trace_bin_size)

        # Combo Box for ps Bins should be an int and have 'ps' present
        self.histBinCombo.addItems(["64 ps", "128 ps", "256 ps"])
        self.histBinCombo.activated.connect(self._model.change_hist_bin_size)

        # Trace Axis Height (cast to int)
        self.traceAxisLine.setText("100")
        self.traceAxisLine.setValidator(QIntValidator(10, 10000, self))
        self.traceAxisLine.editingFinished.connect(self.change_trace_height)

        # Histogram Axis Height (cast to int)
        self.histAxisLine.setText("5")
        self.histAxisLine.setValidator(QIntValidator(1, 10, self))
        self.histAxisLine.editingFinished.connect(self.change_hist_height)

        self.fretButton.clicked.connect(self.change_fret_on)

        self.show()

    def change_fret_on(self):
        if self._model.trace._fret_on == True:
            self._model.trace._fret_on = False
            self.fretButton.setText("OFF")
        else:
            self._model.trace._fret_on = True
            self.fretButton.setText("ON")

    def change_trace_period(self):
        self._model.change_trace_period(self.tracePeriodLine.text())
        
    def change_trace_height(self):
        self.trace.setYRange(0, int(self.traceAxisLine.text()), padding=0)
    
    def change_hist_height(self):
        self.hist.setYRange(0, int(self.histAxisLine.text()), padding=0)

    # changes where the DA signal starts for calculating fret
    def DA_start(self):
        self._model.trace._DA_range[0] = self.green_start.value()/(self._model.measDescRes*1e9)
    
    # changes where the DA signal ends for calculating fret
    def DA_end(self):
        self._model.trace._DA_range[1] = self.green_end.value()/(self._model.measDescRes*1e9)

class View_Backup(QMainWindow):


    def __init__(self, model):
        super().__init__()

        self._model = model
        
        self.win = QtGui.QWidget()

        # Trace Widget with green_line and red_line, with a set Y Range
        self.trace = pg.PlotWidget()
        self.green_trace = self.trace.plot(self._model.trace.period, self._model.trace.green_line, pen='g')
        self.red_trace = self.trace.plot(self._model.trace.period, self._model.trace.red_line, pen='r')
        self.fret_trace = self.trace.plot(self._model.trace.period, self._model.trace.fret_line, pen='b')
        self.trace.setYRange(0, self._model.trace.height, padding=0.005)

        # Histogram Widget with green_hist and red_hist, with a set Y Range
        self.hist = pg.PlotWidget()
        self.green_hist = self.hist.plot(self._model.hist._period, self._model.hist._green_bins, pen='g')
        self.red_hist = self.hist.plot(self._model.hist._period, self._model.hist._red_bins, pen='r')
        self.hist.getPlotItem().setLogMode(x=None, y=True)
        self.hist.setYRange(0, 5, padding=0.01)
        self.hist.setXRange(0, 75, padding=0)

        # lines that can be moved to set DA and DD ranges
        self.green_start = pg.InfiniteLine(pos=5, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="g_start", name="green_start")
        self.green_end = pg.InfiniteLine(pos=35, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="g_end", name="green_end")
        self.red_start = pg.InfiniteLine(pos=40, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="r_start", name="red_start")
        self.red_end = pg.InfiniteLine(pos=65, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="r_end", name="red_end")

        self.hist.addItem(self.green_start)
        self.hist.addItem(self.green_end)
        self.hist.addItem(self.red_start)
        self.hist.addItem(self.red_end)

        # signals when the green lines have changed
        self.green_start.sigPositionChangeFinished.connect(self.DA_start)
        self.green_end.sigPositionChangeFinished.connect(self.DA_end)

        # Trace Period QSpinBox that changes when returnPressed(). Should be a float and have 'ms' present (basically, 1000 ms would be the default value and can't go above. SI unit stays)
        self.tracePeriodLine = TextBox(QIntValidator(1, 1000, self), "trace period (ms) ", self._model.change_trace_period)

        # Combo Box for ms Bins should be an int and have 'ms' present
        self.traceBinCombo = QComboBox(self)
        self.traceBinCombo.addItems(["1 ms", "10 ms", "100 ms"])
        self.traceBinCombo.activated.connect(self._model.change_trace_bin_size)

        # Combo Box for ps Bins should be an int and have 'ps' present
        self.histBinCombo = QComboBox(self)
        self.histBinCombo.addItems(["64 ps", "128 ps", "256 ps"])
        self.histBinCombo.activated.connect(self._model.change_hist_bin_size)

        # Trace Axis Height (cast to int)
        self.traceAxisLine = TextBox(QIntValidator(10, 10000, self), "Height ", self.change_trace_height)

        # Histogram Axis Height (cast to int)
        self.histAxisLine = TextBox(QIntValidator(1, 10, self), "Height ", self.change_hist_height)

        # layout that will be replaced later once Qt creator is used for ui
        self.layout = QtGui.QGridLayout()
        self.win.setLayout(self.layout)

        self.layout.addWidget(self.trace, 0, 0)
        self.layout.addWidget(self.hist, 0, 1)
        self.layout.addWidget(self.tracePeriodLine, 1, 0)
        self.layout.addWidget(self.traceBinCombo, 2, 0)
        self.layout.addWidget(self.histBinCombo, 2, 1)
        self.layout.addWidget(self.traceAxisLine, 3, 0)
        self.layout.addWidget(self.histAxisLine, 3, 1)

        # the widgets that should be created should be:
        # Trace                      Histogram
        # Trace Period
        # ComboBox of ms Bins        ComboBox of ps Bins
        # Axis Height                Axis Height
    def change_trace_height(self, value):
        self.trace.setYRange(0, int(value), padding=0)
    
    def change_hist_height(self, value):
        self.hist.setYRange(0, int(value), padding=0)

    # changes where the DA signal starts for calculating fret
    def DA_start(self):
        self._model.trace._DA_range[0] = self.green_start.value()/(self._model.measDescRes*1e9)
    
    # changes where the DA signal ends for calculating fret
    def DA_end(self):
        self._model.trace._DA_range[1] = self.green_end.value()/(self._model.measDescRes*1e9)