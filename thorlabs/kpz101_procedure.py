# Procedure for KPZ101
import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import pandas as pd 
from numpy import np
from time import sleep
from pymeasure.log import console_log
from pymeasure.instruments.keithley import Keithley2000
from pymeasure.instruments.thorlabs import KPZ101
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, Worker, Procedure, FloatParameter, IntegerParameter
from pymeasure.display import Plotter


class Keithley2100Procedure(Procedure):
    visa = 'USB0::0x05E6::0x2100::1149087::INSTR' 
    address = '29252556'
    wait_time = FloatParameter('Time(s)', units = 's', default = 0.1)
    #voltage_stage = FloatParameter('Voltage (V):Stage', units = 'V', default = 0.0)
    start_freq = FloatParameter('Start Frequency', units = 'Hz', default = 0.0)
    stop_freq = FloatParameter('Stop Frequency', units = 'Hz', default = 750)
    step_size = FloatParameter('Step Size', units = 'Hz', default = 0.266)

    log.info(f"Wait_time initialized to {wait_time}")
    log.info(f"Start frequency initialized to {start_freq}")
    log.info(f"Stop frequency initialized to {stop_freq}")
    log.info(f"Step size initialized to {step_size}")

    DATA_COLUMNS = ['Voltage(V):Stage', 'Voltage(V)']

    def startup(self):
        log.info("Starting up the Keithley 2100 powermeter...")
        self.keithley = Keithley2000(self.visa) 
        self.kpz101 = KPZ101(self.address)
        self.keithley.measure_voltage(0.01, ac = False)
        self.kpz101.move_home()
        sleep(self.wait_time) 
        
        #initialize the instrument
        log.info("Starting up the measurement...")
    def execute(self):
        voltages = np.arange(5, 75, 0.266)

        for voltage in voltages: 
            piezo_voltage = self.kpz101.set_voltage(voltage)
            self.keithley.start_buffer()

            data = {'Voltage (V):Stage': piezo_voltage,
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
            inputs = ['wait_time', 'start_freq', 'stop_freq', 'step_size'] 
            displays = ['wait_time', 'start_freq', 'stop_freq', 'step_size',
                        'voltage'], 
            x_axis = 'Voltage (V):Stage', 
            y_axis = 'Voltage (V)'
        )
        self.setWindowTitle('Measure Interference')

if __name__ == '__main__':
    console_log(log)
    procedure = Keithley2100Procedure() #calling the class procedure
    
    data_filename = 'measure_interference.csv'
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