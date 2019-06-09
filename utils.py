import os
import numpy as np

from datetime import datetime
import openslide
from wsi.slide import downsample
from PIL import Image

from matplotlib import pyplot as plt
from matplotlib import image as mpimage
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

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
    
    return np.array(imgs_array)

def plot_sample_imgs(images, n_rows=2, n_cols=6, size=3, color=True, shuffle=True, 
                     labels=None):
        
    plt.figure(figsize=(n_cols * size, n_rows * size))
    
    for i in range(n_rows * n_cols):
        
        plt.subplot(n_rows, n_cols, i + 1)
        
        if shuffle:
            idx = np.random.randint(0, len(images) - 1)
        else:
            idx = i

        if color:
            plt.imshow(images[idx,:,:,:])
        else:
            plt.imshow(images[idx,:,:,0], cmap=plt.get_cmap("Greys"))
        
        plt.axis('off')
        
        if labels is not None:
            plt.title(labels[idx], fontsize=16)
        else:
            plt.title(str(idx))


def plot_paired_imgs(X_img, Y_img, N, orient='h', size=3, color=True, shuffle=True):
    
    if orient == 'h':
        figsize = (N * size, 2 * size)
    else:
        figsize = (2 * size, N * size)
        
    plt.figure(figsize=figsize)
    
    for i in range(N):
    
        if shuffle:
            idx = np.random.randint(0, len(X_img) - 1)
        else:
            idx = i
        
        # Plot X
        if orient == 'h':
            plt.subplot(2, N, i+1)
        else:
            plt.subplot(N, 2, i*2+1)
        
        if color:
            plt.imshow(X_img[idx,:,:,:])        
        else:
            plt.imshow(X_img[idx,:,:,0], cmap=plt.get_cmap("Greys"))

        plt.axis('off')
        plt.title('X ' + str(idx))
        
        # Plot Y
        if orient == 'h':
            plt.subplot(2, N, i + 1 + N)
        else:
            plt.subplot(N, 2, i*2+2)
            
        if color:
            plt.imshow(Y_img[idx,:,:,:])        
        else:
            plt.imshow(Y_img[idx,:,:,0], cmap=plt.get_cmap("Greys"))
        
        plt.axis('off')
        plt.title('Y ' + str(idx))
        
        

def imscatter(x, y, images, ax=None, zoom=1, lw=0, color='black'):
    
    if ax is None:
        ax = plt.gca()
    
    x, y = np.atleast_1d(x, y)
    artists = []
    
    for x0, y0, image in zip(x, y, images):
        
        image = plt.imread(image)
        im = OffsetImage(image, zoom=zoom)
        
        ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=True, 
                            bboxprops=dict(edgecolor=color, boxstyle="square,pad=0", lw=lw))
        
        artists.append(ax.add_artist(ab))
    ax.update_datalim(np.column_stack([x, y]))
    ax.autoscale()
    return artists