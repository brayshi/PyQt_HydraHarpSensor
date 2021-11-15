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
        self.model = Model(sys_argv)
        self.view = View(self.model)
        
        # start timer to call data from the file every 1 ms
        graphUpdateSpeedMs = 1
        self.timer = QtCore.QTimer(self) # to create a thread that calls a function at intervals
        self.timer.timeout.connect(self.model.frameData) # the update function keeps getting called at intervals
        self.timer.start(graphUpdateSpeedMs)
        self.model.graph_update.connect(self.view_graphs)

        QtGui.QApplication.instance().exec_()

    # used to update the view's trace and histogram plots. processes these events afterwards
    def view_graphs(self):
        self.view.green_trace.setData(self.model.trace.period, self.model.trace.green_line)
        self.view.red_trace.setData(self.model.trace.period, self.model.trace.red_line)
        self.view.fret_trace.setData(self.model.trace.period, self.model.trace.fret_line)

        self.view.green_hist.setData(self.model.hist._period, self.model.hist._green_bins)
        self.view.red_hist.setData(self.model.hist._period, self.model.hist._red_bins)
        self.processEvents()

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit()