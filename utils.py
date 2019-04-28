from datetime import datetime
import openslide
from wsi.slide import downsample

class Timer:
    def __init__(self):
        self.start = datetime.now()
    
    def restart(self):
        self.start = datetime.now()
        
    def elapsed(self, restart=False):
        
        self.end = datetime.now()
        time_elapsed = self.end - self.start
        
        if restart:
            self.restart()
            
        return time_elapsed
