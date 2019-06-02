import PIL
from PIL import Image
import os
import openslide
import numpy as np
import pandas as pd
try:
    get_ipython()
    from tqdm import tqdm_notebook as tqdm
except:
    from tqdm import tqdm

from wsi.filter import filter_greys, filter_whites
from wsi.filter import get_white_pixel_percetange


def _fix_location_bug(location, height_shift, width_shift, level_downsample):

    if (height_shift == 0) & (width_shift != 0):
        location[1] += int(level_downsample)
    elif (height_shift != 0) & (width_shift == 0):
        location[0] += int(level_downsample)

    return location


def _read_patch(image, params, patch_size, output='array'):

    patch_img = image.read_region(params['location'], params['level'], params['level_patch_size'])
    if params['resize'] > 1:
        patch_img = patch_img.resize((patch_size,patch_size), PIL.Image.LANCZOS)

    if output == 'array':
        return np.asarray(patch_img.convert('RGB'))
    else:
        return patch_img


def get_slide_patches_params(image, patch_size, magnification):

    original_magnification = int(image.properties['aperio.AppMag'])
    levels_magnification = [original_magnification/int(x) for x in image.level_downsamples]

    for level, level_magnification in enumerate(levels_magnification):
        if level_magnification >= magnification:
            best_level = level
        else:
            break

    resize = levels_magnification[best_level] / magnification

    level_patch_size = int(round(patch_size * resize))
    level_downsample = image.level_downsamples[best_level]
    level_width, level_height = image.level_dimensions[best_level]

    patches = []

    for height_shift in range(0, int(round(level_height / level_patch_size))):
        for width_shift in range(0, int(round(level_width / level_patch_size))):

            location = [int(width_shift * patch_size * level_downsample), 
                        int(height_shift * patch_size * level_downsample)]

            location = _fix_location_bug(location, height_shift, width_shift, level_downsample)

            patches.append({'index': (height_shift, width_shift),
                            'location': location, 
                            'level': best_level,
                            'level_patch_size': (level_patch_size, level_patch_size),
                            'patch_size': (patch_size, patch_size),
                            'resize': resize})

    return patches


def patch_slide(image, output_dir, patch_size, magnification, white_pixel_thresh=20, 
                sampling=1, white_max_value=220):

    white_pixel_thresh = white_pixel_thresh if white_pixel_thresh else 100

    if isinstance(image, openslide.OpenSlide):
        opeslide_image = image
        file_name = opeslide_image._filename.rsplit('/')[-1] 
    else:
        opeslide_image = openslide.open_slide(image)
        file_name = image.rsplit('/')[-1] 
    
    patches_params = get_slide_patches_params(opeslide_image, patch_size, magnification)

    n_saved = 0
    n_total = 0
    
    for params in patches_params:

        if np.random.uniform() >= sampling:
            continue

        patch_arr = _read_patch(opeslide_image, params, patch_size)
        out_file_name = file_name.replace('.svs', '') + '_{:03d}_{:03d}.png'.format(*params['index'])
        
        blank_pixel_perc = get_white_pixel_percetange(patch_arr, white_max_value)

        if blank_pixel_perc <= white_pixel_thresh:
            patch_img = Image.fromarray(patch_arr)
            patch_img.save(os.path.join(output_dir, out_file_name))
            n_saved += 1
        
        n_total += 1

    return n_total, n_saved


def patch_slides(slide_files, output_dir, patch_size, magnification, 
                 white_pixel_thresh=20, sampling=1, white_max_value=220):

    if isinstance(slide_files, pd.Series):
        slide_files = slide_files.values

    results = []
    for slide_file in tqdm(slide_files):
            
        os_img = openslide.open_slide(slide_file)
        n_patches, n_valid_patches = patch_slide(os_img, output_dir, patch_size, magnification, 
                                                 white_pixel_thresh, sampling, white_max_value)
        
        results.append({'file':slide_file.rsplit('/', 1)[-1], 
                        'total_patches': n_patches, 
                        'valid_patches': n_valid_patches, 
                        'perc_valid_patches': round(n_valid_patches / n_patches, 2)})

    results = pd.DataFrame(results)

    return results