import PIL
from PIL import Image
import os
import openslide
import numpy as np

from wsi.filter import filter_greys, filter_whites
from wsi.filter import get_blank_pixel_percetange


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


def patch_slide(image, output_dir, patch_size, magnification, filter=True, blank_pixel_thresh=30):

    if isinstance(image, openslide.OpenSlide):
        opeslide_image = image
        file_name = opeslide_image._filename.rsplit('/')[-1] 
    else:
        opeslide_image = openslide.open_slide(image)
        file_name = image.rsplit('/')[-1] 
    
    patches_params = get_slide_patches_params(opeslide_image, patch_size, magnification)

    n_saved = 0
    for params in patches_params:

        patch_arr = _read_patch(opeslide_image, params, patch_size)
        out_file_name = file_name.replace('.svs', '') + '_{:02d}_{:02d}.png'.format(*params['index'])

        if filter:
            patch_arr = filter_whites(patch_arr)
            patch_arr = filter_greys(patch_arr, tolerance=100, reverse=False)
            blank_pixel_perc = get_blank_pixel_percetange(patch_arr)

            if blank_pixel_perc <= blank_pixel_thresh:
                patch_img = Image.fromarray(patch_arr)
                patch_img.save(os.path.join(output_dir, out_file_name))
                n_saved += 1

    number_of_patches = len(patches_params)

    return number_of_patches, n_saved