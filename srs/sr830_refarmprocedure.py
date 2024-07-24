import sys
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import numpy as np
from time import sleep

from pymeasure.experiment import (
    Procedure,
    Results,
    FloatParameter,
)
from pymeasure.instruments.srs import SR830
from pymeasure.instruments.thorlabs import KPZ101
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import unique_filename
from pymeasure.display.Qt import QtWidgets


class SR830RefArmProcedure(Procedure):
    lockin_visa = "GPIB0::1::INSTR"  # Adjust the address as necessary
    stage_address = "29252556"

    frequency = FloatParameter("Frequency (Hz)", default=1e3)

    wait_time = FloatParameter("Time(s)", units="s", default=0.1)
    start_voltage = FloatParameter("Start Voltage", units="V", default=0.0)
    stop_voltage = FloatParameter("Stop Voltage", units="V", default=75)
    step_size = FloatParameter("Step Size", units="V", default=0.266)
    time_constant = FloatParameter("Time Constant", units="s", default=0.1)

    log.info(f"Wait_time initialized to {wait_time}")
    log.info(f"Start voltage initialized to {start_voltage}")
    log.info(f"Stop voltage initialized to {stop_voltage}")
    log.info(f"Step size initialized to {step_size}")

    DATA_COLUMNS = ["Reference_Voltage(V)", "Voltage(V)"]

    def startup(self):
        log.info("Starting up the piezostage and lock-in amplifier...")
        self.kpz101 = KPZ101()
        self.lockin = SR830(self.lockin_visa)
        self.lockin.frequency = self.frequency
        # self.lockin.time_constant = self.time_constant / 1e3  # Convert ms to s
        self.kpz101.move_home()
        sleep(self.wait_time)

        # initialize the instrument
        log.info("Starting up the measurement...")

    def execute(self):
        voltages = np.arange(self.start_voltage, self.stop_voltage, self.step_size)

        for voltage in voltages:
            self.kpz101.set_voltage(voltage)
            x = self.lockin.x
            y = self.lockin.y
            sr830_voltage = np.sqrt(x**2 + y**2)

            data = {"Reference_Voltage(V)": voltage, "Voltage(V)": sr830_voltage}
            print(data)  # prints the data

            self.emit("results", data)
            sleep(self.wait_time)

            if self.should_stop():
                log.info("Stopping...")
                break

    def shutdown(self):
        self.kpz101.disconnect()


class MainWindow(ManagedWindow):
    def __init__(self):
        super().__init__(
            procedure_class=SR830RefArmProcedure,
            inputs=[
                "wait_time",
                "start_voltage",
                "stop_voltage",
                "step_size",
                "frequency",
                "time_constant",
            ],
            displays=[
                "wait_time",
                "start_voltage",
                "stop_voltage",
                "step_size",
                "frequency",
            ],
            x_axis="Reference_Voltage(V)",
            y_axis="Voltage(V)",
        )

        self.setWindowTitle("SR830 Lock-In Amplifier Measurement with Reference Arm")

        self.filename = r"V_refV_"  # Sets default filename
        self.directory = (
            r"c:\Users\DK-microscope\Documents\temp"  # Sets default directory
        )
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
