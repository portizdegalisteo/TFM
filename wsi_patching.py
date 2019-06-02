import yaml
import os
import argparse
import openslide
import pandas as pd
try:
    get_ipython()
    from tqdm import tqdm_notebook as tqdm
except:
    from tqdm import tqdm

from wsi.slide import thumbnail
from wsi.patch import patch_slides

def main(args):

    with open(args.conf, 'r') as f:
        conf = yaml.load(f)

    slides_path = os.path.join(conf['data_path'], 'slides', 'svs')

    slides_df = pd.read_csv(os.path.join(conf['data_path'], 'slides_metadata.csv'), sep='|')
    slides_df = slides_df[slides_df['file_name'].isin(os.listdir(slides_path))]

    # Thumbnails
    if args.thumbnails:

        thumbnails_path = os.path.join(conf['data_path'], 'slides', 'thumbnail')
        if not os.path.exists(thumbnails_path):
            os.mkdir(thumbnails_path)

        for slide_file in tqdm(slides_df['file_name'].values, unit='file'):
            os_img = openslide.open_slide(os.path.join(slides_path, slide_file))
            img = thumbnail(os_img, max_size=conf['wsi']['thumbnail_size'])
            img.save(os.path.join(thumbnails_path, slide_file.replace('.svs', '.png')))

    # Patches
    patches_path = os.path.join(conf['data_path'], 'slides', 'patches')
    if not os.path.exists(patches_path):
        os.mkdir(patches_path)

    slide_files = slides_df['file_name'].map(lambda x: os.path.join(slides_path, x))
    patching_results = patch_slides(slide_files, patches_path, 
                                    conf['wsi']['patch_size'], 
                                    conf['wsi']['magnification'], 
                                    conf['wsi']['white_pixel_threshold'], 
                                    conf['wsi']['sampling'])
    
    patching_results.to_csv(os.path.join(conf['data_path'], 'patching_results.csv'), sep='|', index=False)


if __name__ == "__main__":

    parser = argparse.ArgumentParser("WSI Patching")
    parser.add_argument('-conf', help="Path to config file", type=str, default='conf/user_conf.yaml')
    parser.add_argument('-thumbnails', help="Create thumbail .png images", type=bool, default=True)

    args = parser.parse_args()

    main(args)