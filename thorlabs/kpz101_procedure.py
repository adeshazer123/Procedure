# Procedure for KPZ101
import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import sys

import pandas as pd 
import numpy as np
from time import sleep
from pymeasure.log import console_log
from pymeasure.instruments.keithley import Keithley2000
from pymeasure.instruments.thorlabs import KPZ101
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.Qt import QtWidgets

from pymeasure.experiment import Results, Worker, Procedure, FloatParameter, IntegerParameter
from pymeasure.display import Plotter


class Keithley2100Procedure(Procedure):
    visa = 'USB0::0x05E6::0x2100::1149087::INSTR' 
    #address = '29252556'
    wait_time = FloatParameter('Time(s)', units = 's', default = 0.1)
    #voltage_stage = FloatParameter('Voltage (V):Stage', units = 'V', default = 0.0)
    start_voltage = FloatParameter('Start Voltage', units = 'V', default = 0.0)
    stop_voltage = FloatParameter('Stop Voltage', units = 'V', default = 75)
    step_size = FloatParameter('Step Size', units = 'V', default = 0.266)

    # log.info(f"Wait_time initialized to {wait_time}")
    log.info(f"Start voltage initialized to {start_voltage}")
    log.info(f"Stop voltage initialized to {stop_voltage}")
    log.info(f"Step size initialized to {step_size}")

    DATA_COLUMNS = ['Voltage(V):Stage', 'Voltage(V)']

    def startup(self):
        log.info("Starting up the Keithley 2100 powermeter...")
        self.keithley = Keithley2000(self.visa) 
        self.kpz101 = KPZ101()
        self.keithley.measure_voltage(0.01, ac = False)
        self.kpz101.move_home()
        sleep(self.wait_time) 
        
        #initialize the instrument
        log.info("Starting up the measurement...")
    def execute(self):
        voltages = np.arange(self.start_voltage, self.stop_voltage, self.step_size)

        for voltage in voltages: 
            self.kpz101.set_voltage(voltage)
            self.keithley.start_buffer()
            # piezo_voltage = self.kpz101.get_voltage

            data = {'Voltage(V):Stage': voltage, #piezo_voltage,
                'Voltage(V)': self.keithley.voltage
            }
            print(data)
            self.emit('results', data)
            sleep(self.wait_time)
            
            if self.should_stop():
                log.info("Stopping...")
                break 
    
    def shutdown(self): 
        pass
class MainWindow(ManagedWindow):
    def __init__(self): 
        super().__init__(procedure_class = Keithley2100Procedure, 
            inputs = ['wait_time', 'start_voltage', 'stop_voltage', 'step_size'],
            displays = ['wait_time', 'start_voltage', 'stop_voltage', 'step_size'], 
            x_axis = 'Voltage(V):Stage', 
            y_axis = 'Voltage(V)'
        )
        self.setWindowTitle('Measure Interference')

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())  

    # console_log(log)
    # procedure = Keithley2100Procedure() #calling the class procedure
    
    # data_filename = 'measure_interference.csv'
    # log.info("Constructing the Results with a data file: %s" % data_filename)
    # results = Results(procedure, data_filename)
    # log.info("Results created")

    # plotter = Plotter(results) 
    # log.info("Plotter created")
    # plotter.start() 

    # log.info("Creating the worker...")
    # worker = Worker(results)
    # log.info("Worker created")
    # worker.start()
    # worker.join(timeout = 3600) #timeout in seconds
    # log.info("Measurement is finished.")