from datetime import datetime
import openslide
from wsi.slide import downsample
from PIL import Image

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


def display_image_array(img_array, display_size=(400,400)):
    return Image.fromarray(img_array).resize(display_size)