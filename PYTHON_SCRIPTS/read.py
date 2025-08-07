import sys
import serial
import struct
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

class SerialPlotter(QtWidgets.QMainWindow):
    def __init__(self, port='/dev/ttyACM4', baudrate=115200):
        super().__init__()

        self.ser = serial.Serial(port, baudrate, timeout=1)
        self.buffer_size = 8000  # bytes
        self.num_points = 4000   # uint16_t
        self.start_marker = [0xDE, 0xAD, 0xBE, 0xEF]

        # Set up plot
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.plot_data = self.plot_widget.plot(pen='y')

        self.plot_widget.setYRange(0, 4000)  # uint16_t full range
        self.plot_widget.setTitle("Live Serial Plot")
        self.plot_widget.showGrid(x=True, y=True)

        # Timer to update plot
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(10)  # check every 10ms

    def read_frame(self):
        # Try to detect start marker
        while True:
            byte = self.ser.read(1)
            if not byte:
                return None  # timeout

            if byte[0] == self.start_marker[0]:
                rest = self.ser.read(3)
                if rest == bytes(self.start_marker[1:]):
                    return self.ser.read(self.buffer_size)
    
    def update_plot(self):
        raw = self.read_frame()
        if raw and len(raw) == self.buffer_size:
            data = struct.unpack('<' + 'H'*self.num_points, raw)
            self.plot_data.setData(data)

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = SerialPlotter()
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
