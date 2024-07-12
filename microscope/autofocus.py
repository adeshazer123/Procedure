# Purpose: Procedure to control the microscope 
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from pymeasure.experiment import Procedure

class AutofocusProcedure(Procedure):
    def __init__(self): 
        self.microscope = None
