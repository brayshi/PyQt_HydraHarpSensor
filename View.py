from PyQt5 import uic
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QFileDialog, QMainWindow
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
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
        self.green_trace = self.trace.plot(self._model.trace.period, self._model.trace.green_line, pen='g')
        self.red_trace = self.trace.plot(self._model.trace.period, self._model.trace.red_line, pen='r')
        self.fret_trace = self.trace.plot(self._model.trace.period, self._model.trace.fret_line, pen='b')
        self.trace.setYRange(0, 100, padding=0)
        self.trace.setLabels(title='Trace Graph', left='photons per bin', bottom='time (ms)')

        # Histogram Widget with green_hist and red_hist, with a set Y Range
        self.hist.setMouseEnabled(x=False, y=False)
        self.green_hist = self.hist.plot(self._model.hist._period, self._model.hist._green_bins, pen='g')
        self.red_hist = self.hist.plot(self._model.hist._period, self._model.hist._red_bins, pen='r')
        self.hist.getPlotItem().setLogMode(x=None, y=True)
        self.hist.setYRange(0, 5, padding=0)
        self.hist.setXRange(0, 75, padding=0)
        self.hist.setLabels(title='Histogram', left='photons per bin', bottom='time (ns)')

        # lines that can be moved to set DA and DD ranges
        self.donor_start = pg.InfiniteLine(pos=5, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="d_start", name="green_start")
        self.donor_end = pg.InfiniteLine(pos=35, angle=90, pen='g', movable=True, bounds=[0,75], hoverPen='b', label="d_end", name="green_end")
        self.acceptor_start = pg.InfiniteLine(pos=40, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="a_start", name="red_start")
        self.acceptor_end = pg.InfiniteLine(pos=65, angle=90, pen='r', movable=True, bounds=[0,75], hoverPen='b', label="a_end", name="red_end")

        self.hist.addItem(self.donor_start)
        self.hist.addItem(self.donor_end)
        self.hist.addItem(self.acceptor_start)
        self.hist.addItem(self.acceptor_end)

        # signals when the green lines have changed
        self.donor_start.sigPositionChangeFinished.connect(self.DA_start)
        self.donor_end.sigPositionChangeFinished.connect(self.DA_end)

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

        self.coarseTraceLine.setText("1800")
        self.coarseTraceLine.setValidator(QIntValidator(1, 7200, self))

        self.coarseTraceButton.clicked.connect(self.change_trace_graph)

        self.fileButton.clicked.connect(self.change_file)

        self.resetCoarseButton.clicked.connect(self.reset_coarse_graph)

        self.coarseScaleButton.clicked.connect(self.scale_graph)

        self.resetHistButton.clicked.connect(self.reset_hist)

    # change file being tailed by model
    def change_file(self):
        file = QFileDialog.getOpenFileName(self, "Open PTU file", "This PC", "PTU files (*.ptu)")
        self._model.inputFile = ReadFile.confirmHeader(file)
        self.reset_hist()
        self.reset_coarse_graph()
        self.fileButton.setText(file[0])

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
                self._model.coarse_binning = CoarseBinning(int(self.coarseTraceLine.text()))
            self._model.coarse_on = True
            self.coarseTraceButton.setText("ON (running)")
            self.trace.setLabels(title='Coarse Trace Graph', left='photons per 1 s bin', bottom='time (s)')
            self._model.coarse_graph_update.emit()
            self.trace.setXRange(0, self._model.coarse_binning._seconds, padding=0)
        elif self._model.coarse_on == True:
            self._model.coarse_on = False
            self.coarseTraceButton.setText("OFF (running)")
            self.trace.setLabels(title='Trace Graph', left='photons per bin', bottom='time (ms)')
            self._model.trace_update.emit()
            self.trace.setXRange(0, int(self.tracePeriodLine.text())/1000, padding=0)

    def reset_coarse_graph(self):
        self._model.coarse_binning = None
        self.coarseTraceButton.setText("OFF")
        self._model.coarse_on = False
        self._model.coarse_indx = 0
        self._model.coarse_ofl = 0
        self.trace.setLabels(title='Trace Graph', left='photons per bin', bottom='time (ms)')
        self._model.trace_update.emit()
        self.trace.setXRange(0, int(self.tracePeriodLine.text())/1000, padding=0)
        if (self._model._scaling_on == True):
            self.trace.setYRange(0, self._model.trace._max_height*1.2, padding=0)
        else:
            self.trace.setYRange(0, int(self.traceAxisLine.text()), padding=0)

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
        self._model.hist._measDescRes = ReadFile.readHeader(self._model.inputFile)
        self._model.hist.change_hist()

    # change trace period that will be displayed for the next frame
    def change_trace_period(self):
        self._model.change_trace_period(self.tracePeriodLine.text())
    
    # change trace graph's height
    def change_trace_height(self):
        if (self._model.coarse_binning == None and self._model._scaling_on == False):
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