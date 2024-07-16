# Author: Amelie Deshazer 
# Date: 2024-07-16 
# Purpose: Camera procedure to control the camera 


import logging 
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

#Author: Amelie Deshazer 
#Date: 2024-07-03 
#Purpose: Procedure for controlling keithley 2100 powermeter. 


import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import pandas as pd 
import time 
import c2 as cv2
from time import sleep
from pymeasure.log import console_log
from pymeasure.instruments.thorlabs import CS165MUM
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, Worker, Procedure, FloatParameter, IntegerParameter
from pymeasure.display import Plotter


class Keithley2100Procedure(Procedure):
    camera_visa = 0 #must add visa address
    stage_visa = 
    #wait_time = FloatParameter('Time', units = 's', default = 0.01)
    log.info(f"Wait_time initialized to {visa}")
    exposure_time = FloatParameter('Exposure Time', units = 's', default = 0.01)
    DATA_COLUMNS = ['Time(s)', 'Voltage(V)']

    def startup(self):
        log.info("Starting up Thorlabs Color Camera...")
        self.camera = CS165MUM(self.visa) 
        image = self.camera.image_acquire()
        sleep(0.01)
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) #convert array from RGB to BGR
        cv2.imshow('image', image_bgr)
        
        #initialize the instrument
        log.info("Starting up the measurement...")

        #focus 

        stage = 
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

class CovertRGBtoBGR:
    def __init__(self):
        pass
    def covert(self, image):
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)