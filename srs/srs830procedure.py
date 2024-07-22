import numpy as np
import time
import sys

from pymeasure.experiment import (
    Procedure,
    Results,
    FloatParameter,
    IntegerParameter,
)
from pymeasure.instruments.srs import SR830
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import unique_filename
from pymeasure.display.Qt import QtWidgets

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SR830Procedure(Procedure):
    lockin_visa = "GPIB::8"  # Adjust the address as necessary

    frequency = FloatParameter("Frequency (Hz)", default=1e3)
    time_constant = IntegerParameter("Time Constant (ms)", default=1000)
    interval = FloatParameter("Interval between measurements (s)", default=0.050)
    duration = FloatParameter("Total Duration (s)", default=10.0)

    DATA_COLUMNS = ["Time (s)", "Voltage (V)"]

    def startup(self):
        self.lockin = SR830(self.lockin_visa)
        self.lpkin.frequency = self.frequency
        self.lockin.time_constant = self.time_constant / 1e3  # Convert ms to s

    def execute(self):

        start_time = time.time()
        while (time.time() - start_time) < self.duration:
            x = self.lockin.x
            y = self.lockin.y
            voltage = np.sqrt(x**2 + y**2)
            self.emit(
                "results",
                {
                    "Time (s)": time.time() - start_time,
                    "Voltage (V)": voltage,
                },
            )
            time.sleep(self.interval)

            if self.should_stop():
                break

    def shutdown(self):
        log.info("shutting down")


class MainWindow(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class=SR830Procedure,
            inputs=["frequency", "time_constant", "interval", "duration"],
            displays=["frequency", "time_constant", "interval", "duration"],
            x_axis="Time (s)",
            y_axis="Voltage (V)",
        )
        self.setWindowTitle("SR830 Lock-In Amplifier Measurement")

        self.filename = r"xy_"  # Sets default filename
        self.directory = r"/home/daichi/Documents/temp"  # Sets default directory
        self.store_measurement = True  # Controls the 'Save data' toggle
        self.file_input.extensions = [
            "csv",
            "dat",
        ]  # Sets recognized extensions, first entry is the default extension
        self.file_input.filename_fixed = (
            False  # Controls whether the filename-field is frozen (but still displayed)
        )

    def queue(self):
        filename = unique_filename(self.directory, self.filename)
        procedure = self.make_procedure()
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)
        self.manager.queue(experiment)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
