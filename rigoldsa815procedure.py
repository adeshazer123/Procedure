# Purpose: Set up a procedure for the Rigol DSA815


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.display import Plotter
from pymeasure.experiment import Procedure, FloatParameter, IntegerParameter, Worker, Results
from pymeasure.instruments import DSA815
from time import sleep



class DSA815Procedure(Procedure):
    serial_address = 'USB0::0x1AB1::0x09C4::DSA8A192800001::INSTR' 
    log.info(f"Serial address initialized to {serial_address}")

    start_freq = FloatParameter('Start Frequency', units = 'Hz', default =0)
    center_freq = FloatParameter('Center Frequency', units = 'Hz', default = 5e6)
    stop_freq = FloatParameter('Stop Frequency', units = 'Hz', default = 10e6)
    sweep_time = FloatParameter('Sweep Time', units = 's', default = 0.01)
    data_points = IntegerParameter('Data Points', default = 3001)
  
    DATA_COLUMNS = ['Frequency (Hz)', 'Amplitude (dBm)']

    def startup(self): 
        log.info("Starting up the Rigol DSA815 spectrum analyzer...")
        self.dsa815 = DSA815(self.serial_address)
        log.info("Starting up the measurement...")

    def execute(self):
        data = self.dsa815.trace_df()
        for i in range(self.data_points):
            data = {'Frequency (Hz)': data[0][i], 'Amplitude (dBm)': data[1][i]}
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(0.01)
            if self.should_stop():
                log.warning("Received stop request")
                break
def shutdown(self): 
        pass
class ManagedWindow(ManagedWindow):
    def __init__(self): 
        super().__init__(procedure_class = Keithley2100Procedure, 
            inputs = ['wait_time'], 
            displays = ['wait_time', 'voltage'], 
            x_axis = 'Frequency (Hz)', 
            y_axis = 'Amplitude (dBm)'
        )
        self.setWindowTitle('Rigol DSA815 Spectrum Analyzer')

if __name__ == '__main__':
    console_log(log)
    procedure = DSA815Procedure() #calling the class procedure
    
    data_filename = 'dsa815procedure.csv'
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

