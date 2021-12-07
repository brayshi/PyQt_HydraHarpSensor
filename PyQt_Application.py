import sys
from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore, QtGui
from Model import Model
from View import View
import sys

class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)
        # instantiate model and view. Show application window
        self.model = Model()
        self.view = View(self.model)
        
        # start timer to call data from the file every 1 ms
        graphUpdateSpeedMs = 1
        self.timer = QtCore.QTimer(self) # to create a thread that calls a function at intervals
        self.timer.timeout.connect(self.model.frameData) # the update function keeps getting called at intervals
        self.timer.start(graphUpdateSpeedMs)
        self.model.trace_update.connect(self.view_trace)
        self.model.hist_update.connect(self.view_hist)
        self.model.coarse_graph_update.connect(self.view_coarse_graph)

        QtGui.QApplication.instance().exec_()

    # used to update the view's trace and histogram plots. processes these events afterwards
    def view_trace(self):
        self.view.green_trace.setData(self.model.trace.period, self.model.trace.green_line)
        self.view.red_trace.setData(self.model.trace.period, self.model.trace.red_line)
        self.view.fret_trace.setData(self.model.trace.period, self.model.trace.fret_line)
        self.processEvents()

    def view_hist(self):
        self.view.green_hist.setData(self.model.hist._period, self.model.hist._green_bins)
        self.view.red_hist.setData(self.model.hist._period, self.model.hist._red_bins)
        self.processEvents()

    def view_coarse_graph(self):
        self.view.green_trace.setData(self.model.coarse_binning.period[:self.model.coarse_indx], self.model.coarse_binning.green_line[:self.model.coarse_indx])
        self.view.red_trace.setData(self.model.coarse_binning.period[:self.model.coarse_indx], self.model.coarse_binning.red_line[:self.model.coarse_indx])
        self.view.fret_trace.setData(self.model.coarse_binning.period[:self.model.coarse_indx], self.model.coarse_binning.fret_line[:self.model.coarse_indx])
        if (self.model.coarse_binning._max_height * 1.2 <= self.model.coarse_binning._green_line[self.model.coarse_indx] and self.model.coarse_binning._scaling_on == True):
            self.model.coarse_binning._max_height = self.model.coarse_binning._green_line[self.model.coarse_indx]
            self.view.trace.setYRange(0, self.model.coarse_binning._max_height, padding=0)
        self.processEvents()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit()