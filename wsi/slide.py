import PIL
import numpy as np
import openslide

def thumbnail(openslide_img, max_size=512, resample=PIL.Image.LANCZOS):

    level = openslide_img.level_count - 1
    width,height = openslide_img.level_dimensions[level]
    
    scale_factor = max(width/max_size, height/max_size)
    new_width = int(round(width / scale_factor))
    new_height = int(round(height / scale_factor))

    img = openslide_img.read_region((0,0), level, (width,height))
    img = img.resize((new_width, new_height), resample)

    return img 
    

def downsample(openslide_img, scale_factor, output_format='image'):

    level = openslide_img.get_best_level_for_downsample(scale_factor)
    level_dim = openslide_img.level_dimensions[level]

    ws_img = openslide_img.read_region((0,0), level, level_dim)
    ws_img = ws_img.convert("RGB")

    new_dim = tuple(int(d/scale_factor) for d in openslide_img.dimensions)
    img = ws_img.resize(new_dim, PIL.Image.BILINEAR)

    if output_format == 'image':
        return img
    else:        
        return np.asarray(img)


def svs_to_png(file, scale_factor=32, downsampling=True):
    
    os_img = openslide.open_slide(file['input'])
    
    scale_factor = 1 if not downsampling else scale_factor
    img = downsample(os_img, scale_factor, output_format='image')
    
    img.save(file['output'])

    return True
