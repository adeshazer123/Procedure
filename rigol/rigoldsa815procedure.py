# Purpose: Set up a procedure for the Rigol DSA815


import logging
import sys
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.display.windows import ManagedWindow
from pymeasure.display.Qt import QtWidgets
from pymeasure.experiment import Procedure, FloatParameter, IntegerParameter
from pymeasure.instruments.rigol import DSA815
from time import sleep



class DSA815Procedure(Procedure):
    serial_address = 'USB0::0x1AB1::0x0960::DSA8A154202508::INSTR' 
    log.info(f"Serial address initialized to {serial_address}")

    start_freq = FloatParameter('Start Frequency', units = 'Hz', default =0)
    center_freq = FloatParameter('Center Frequency', units = 'Hz', default = 5e6)
    stop_freq = FloatParameter('Stop Frequency', units = 'Hz', default = 10e6)
    sweep_time = FloatParameter('Sweep Time', units = 's', default = 0.01)
    data_points = IntegerParameter('Data Points', default = 601)
  
    DATA_COLUMNS = ['Frequency (Hz)', 'Amplitude (dBm)']

    def startup(self): 
        log.info("Starting up the Rigol DSA815 spectrum analyzer...")
        self.dsa815 = DSA815(self.serial_address)
        self.dsa815.frequency_points = self.data_points
        log.info("Starting up the measurement...")

    def execute(self):
        data_df = self.dsa815.trace_df()
        for i in range(self.data_points):
            data = {'Frequency (Hz)': data_df.iloc[i,0], 'Amplitude (dBm)': data_df.iloc[i,1]}
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
        super().__init__(procedure_class = DSA815Procedure, 
            inputs = ['start_freq', 'center_freq', 'stop_freq', 'sweep_time', 'data_points'], 
            displays = ['start_freq', 'center_freq', 'stop_freq', 'sweep_time', 'data_points'], 
            x_axis = 'Frequency (Hz)', 
            y_axis = 'Amplitude (dBm)'
        )
        self.setWindowTitle('Rigol DSA815 Spectrum Analyzer')

if __name__ == '__main__':
    console_log(log)
    app = QtWidgets.QApplication(sys.argv)
    window = ManagedWindow()
    window.show()
    sys.exit(app.exec()) 


    # procedure = DSA815Procedure() #calling the class procedure
    
    # data_filename = 'dsa815procedure.csv'
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

