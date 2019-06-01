import os
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import image as mpimage
from datetime import datetime
import openslide
from wsi.slide import downsample
from PIL import Image

try:
    get_ipython()
    from tqdm import tqdm_notebook as tqdm
except:
    from tqdm import tqdm


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


def read_images(filenames, directory=None):

    imgs_array = []

    for filename in tqdm(filenames, unit='imgs'):
        filename = os.path.join(directory, filename) if directory else filename
        img_array = mpimage.imread(filename)
        imgs_array.append(img_array)
    
    return imgs_array

def plot_sample_imgs(images, n_rows=2, n_cols=6, size=3, color=True):
        
    plt.figure(figsize=(n_cols * size, n_rows * size))
    
    for i in range(n_rows * n_cols):
        
        plt.subplot(n_rows, n_cols, i + 1)
        
        idx = np.random.randint(0, len(images) -1)
        if color:
            plt.imshow(images[idx,:,:,:])
        else:
            plt.imshow(images[idx,:,:,0], cmap=plt.get_cmap("Greys"))
        
        plt.axis('off')
        plt.title(str(idx))


def plot_paired_imgs(X_img, Y_img, N, orient='h', size=3, color=True):
    
    if orient == 'h':
        figsize = (N * size, 2 * size)
    else:
        figsize = (2 * size, N * size)
        
    plt.figure(figsize=figsize)
    
    for i in range(N):
    
        idx = np.random.randint(0, len(X_img - 1))
        
        if orient == 'h':
            plt.subplot(2, N, i+1)
        else:
            plt.subplot(N, 2, i*2+1)
        
        if color:
            plt.imshow(X_img[idx,:,:,0], cmap=plt.get_cmap("Greys"))
        else:
            plt.imshow(X_img[idx,:,:,:])

        plt.axis('off')
        plt.title('X ' + str(idx))
        
        if orient == 'h':
            plt.subplot(2, N, i + 1 + N)
        else:
            plt.subplot(N, 2, i*2+2)
            
        if color:
            plt.imshow(Y_img[idx,:,:,0], cmap=plt.get_cmap("Greys"))
        else:
            plt.imshow(Y_img[idx,:,:,:])        
        
        plt.axis('off')
        plt.title('Y ' + str(idx))