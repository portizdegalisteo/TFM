from skimage.morphology import remove_small_objects
import numpy as np
from PIL import Image

def rgb_to_gray(rgb):
    gray = np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
    return gray

def filter_whites(rgb, maximum=220, filter_color=[0,0,0]):
    
    gray = rgb_to_gray(rgb)
    mask = gray > maximum
    
    rgb.setflags(write=1)
    rgb[mask,:] = filter_color
    rgb.setflags(write=0)
    
    return rgb

def filter_greys(rgb, tolerance=15, reverse=False):
    """
    Create a mask to filter out pixels where the red, green, and blue channel values are similar.

    Args:
    tolerance: Tolerance value to determine how similar the values must be in order to be filtered out
    """
    
    rg_diff = abs(rgb[:, :, 0] - rgb[:, :, 1]) <= tolerance
    rb_diff = abs(rgb[:, :, 0] - rgb[:, :, 2]) <= tolerance
    gb_diff = abs(rgb[:, :, 1] - rgb[:, :, 2]) <= tolerance
    
    mask = ~(rg_diff & rb_diff & gb_diff)
    mask = ~mask if reverse else mask
        
    rgb = rgb * np.dstack([mask, mask, mask])
       
    return rgb


def get_blank_pixel_percetange(img):
    
    blank_pixels = (img <= 0).sum()
    total_pixels = img.size
    percetange_zero = round(100 * blank_pixels / total_pixels, 2)
    
    return percetange_zero