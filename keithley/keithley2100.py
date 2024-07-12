#Author: Amelie Deshazer 
#Date: 2024-07-03 
#Purpose: Procedure for controlling keithley 2100 powermeter. 


import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import pandas as pd 
import time 
from time import sleep
from pymeasure.log import console_log
from pymeasure.instruments.keithley import Keithley2000
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, Worker, Procedure, FloatParameter, IntegerParameter
from pymeasure.display import Plotter


class Keithley2100Procedure(Procedure):
    visa = 'USB0::0x05E6::0x2100::1149087::INSTR' #must add visa address
    wait_time = FloatParameter('Time', units = 's', default = 0.01)
    log.info(f"Wait_time initialized to {wait_time}")

    DATA_COLUMNS = ['Time(s)', 'Voltage(V)']

    def startup(self):
        log.info("Starting up the Keithley 2100 powermeter...")
        self.keithley = Keithley2000(self.visa) 
        self.keithley.measure_voltage(0.01, ac = False)
        sleep(self.wait_time) 
        
        #initialize the instrument
        log.info("Starting up the measurement...")
    def execute(self):
        time_0 = time.time()
        while True:
            time_1 = time.time()
            self.keithley.start_buffer()
            dtime = time_1 - time_0 #measure time elapsed
            data = {'Time (s)': dtime,
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
class ManagedWindow(ManagedWindow):
    def __init__(self): 
        super().__init__(procedure_class = Keithley2100Procedure, 
            inputs = ['wait_time'], 
            displays = ['wait_time', 'voltage'], 
            x_axis = 'Time (s)', 
            y_axis = 'Voltage (V)'
        )
        self.setWindowTitle('Keithley 2100 Powermeter')

if __name__ == '__main__':
    console_log(log)
    procedure = Keithley2100Procedure() #calling the class procedure
    
    data_filename = 'keithley2.csv'
    log.info("Constructing the Results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)
    log.info("Results created")

    plotter = Plotter(results) 
    log.info("Plotter created")
    plotter.start() 

    log.info("Creating the worker...")
    worker = Worker(results)
    log.info("Worker created")
    worker.start()
    worker.join(timeout = 3600) #timeout in seconds
    log.info("Measurement is finished.")