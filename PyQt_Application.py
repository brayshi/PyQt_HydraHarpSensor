import sys
from PyQt5.QtWidgets import QApplication
from pyqtgraph.Qt import QtCore, QtGui
from Model import Model
from View import View

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
        self.model.coarse_graph_update.connect(self.view_new_coarse_graph)
        self.model.coarse_graph_show.connect(self.view_old_coarse_graph)
        self.model.label_update.connect(self.view_labels)

        QtGui.QApplication.instance().exec_()

    # used to update the view's trace and histogram plots. processes these events afterwards
    def view_trace(self):
        self.view.donor_trace.setData(self.model.trace.period, self.model.trace.green_line)
        self.view.acceptor_trace.setData(self.model.trace.period, self.model.trace.red_line)
        self.view.fret_trace.setData(self.model.trace.period, self.model.trace.fret_line)
        if (self.model._scaling_on == True):
            self.view.trace.setYRange(0, self.model.trace._prev_max_height*1.2, padding=0)
        self.view.trace.setXRange(0, int(self.model.trace._period_milliseconds)/1000, padding=0)
        self.view.trace.setLabels(title='Trace Graph', left='photons per ' + str(self.model.trace._bin_size_milliseconds) + ' ms bin', bottom='time (ms)')
        self.processEvents()

    def view_hist(self):
        self.view.donor_hist.setData(self.model.hist._period, self.model.hist._green_bins)
        self.view.acceptor_hist.setData(self.model.hist._period, self.model.hist._red_bins)
        self.view.hist.setLabels(title='Histogram', left='photons per ' + str(self.model.hist._bin_size_picoseconds) + ' ps bin', bottom='time (ns)')
        self.processEvents()

    def view_new_coarse_graph(self):
        self.view_coarse_graph(self.model.coarse_indx + 1)
    
    def view_old_coarse_graph(self):
        self.view_coarse_graph(self.model.coarse_indx)

    def view_coarse_graph(self, value):
        self.view.donor_trace.setData(self.model.coarse_binning.period[:value], self.model.coarse_binning.donor_line[:value])
        self.view.acceptor_trace.setData(self.model.coarse_binning.period[:value], self.model.coarse_binning.acceptor_line[:value])
        self.view.fret_trace.setData(self.model.coarse_binning.period[:value], self.model.coarse_binning.fret_line[:value])
        if (self.model._scaling_on == True):
            self.view.trace.setYRange(0, self.model.coarse_binning._max_height*1.2, padding=0)
        self.processEvents()


    def view_labels(self):
        self.view.donorCountsLabel_2.setText(str(self.model.donor_counts) + "/s")
        self.view.acceptorCountsLabel_2.setText(str(self.model.acceptor_counts) + "/s")
        if (self.model.trace._fret_on == True or self.model.coarse_binning):
            self.view.fretCountsLabel_2.setText(str(self.model.fret_counts) + "/s")
        else:
            self.view.fretCountsLabel_2.setText("NA")

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit()