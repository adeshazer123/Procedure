# Purpose: Set up a procedure for the Rigol DSA815


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from pymeasure.experiment import Procedure


class DSA815Procedure(Procedure):
    serial_address = 'USB0::0x1AB1::0x09C4::DSA8A192800001::INSTR' 
    log.info(f"Serial address initialized to {serial_address}")

    #start_freq = FloatParameter('Start Frequency', units = 'Hz', default =0)
    #center_freq = FloatParameter('Center Frequency', units = 'Hz', default = 5e6)
    #stop_freq = FloatParameter('Stop Frequency', units = 'Hz', default = 10e6)
    #sweep_time = FloatParameter('Sweep Time', units = 's', default = 0.01)
    #data_points = IntegerParameter('Data Points', default = 3001)
  
    DATA_COLUMNS = ['Frequency (Hz)', 'Amplitude (dBm)']

    def startup(self): 
        log.info("Starting up the Rigol DSA815 spectrum analyzer...")
        self.dsa815 = DSA815(self.serial_address)
        self.dsa815.initialize()
        log.info("Starting up the measurement...")

