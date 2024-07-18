# Author: Amelie Deshazer 
# Date: 2024-07-16 
# Purpose: Camera procedure to control the camera's focus

import logging 

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

import pandas as pd 
import time 
import c2 as cv2
from time import sleep
from pymeasure.log import console_log
from pymeasure.instruments.thorlabs import CS165MUM, KDC101
from procedure.microscope.focus import Focus
from pymeasure.display.windows import ManagedWindow
from pymeasure.experiment import Results, Worker, Procedure, FloatParameter, IntegerParameter
from pymeasure.display import Plotter
n
class AutofocusProcedure(Procedure):
    stage_visa = 'KDC101' #must add address 
    camera_visa = "" #must add address

    exposure_time = FloatParameter('Exposure Time', units = 's', default = 0.01)
    initial_position = FloatParameter('Initial Position', units = 'mm', default = 0)

    

    def startup(self): 
        self.stage = KDC101(self.stage_visa)
        log.info("Starting up the KDC101 stage...")

        self.camera = CS165MUM(self.camera_visa)
        log.info("Starting up the Thorlabs Color Camera...")

        self.stage.load_config()
        log.info("Stage configuration loaded")

         #need to load intended stage configuration
        #self.stage.move_home() #move stage to home position
    
    def execute(self): 
        z_positions = self.stage.move_home()
        for z in z_positions:
            self.stage.move_relative(z)
            image = self.camera.image_acquire()
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 
            focus = Focus()
            focus_score = focus.calculate_focus_score(image_bgr)

            data = {'Z Position (mm)': z, 
                    'Focus Score': focus_score}
            
            print(data)
            self.emit('results', data)
    
    def shutdown(self): 
        self.stage.disconnect()
        #add camera disconnect

class ManagedWindow(ManagedWindow): 
    def __init__(self): 
        super().__init__(procedure_class = AutofocusProcedure, 
            inputs = ['exposure_time', 'initial_position'], 
            displays = ['initial_position', 'focus_score'], 
            x_axis = 'Position (mm)', 
            y_axis = 'Focus Score'
        )
        self.setWindowTitle('Focus Score')

if __name__ == '__main__':
    console_log(log)
    procedure = AutofocusProcedure() #calling the class procedure
    
    data_filename = 'Autofocus.csv'
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