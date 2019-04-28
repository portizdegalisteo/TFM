import argparse
import os
import re
import yaml
import pandas as pd

from gdc.download import api_download_iterative
from gdc.utils import gunzip

def print_summary(df, gb_field):

    summary = df.groupby(gb_field).agg({'file_name': 'size', 'file_size': 'sum'})
    summary = summary.rename(columns={'file_name': 'count', 'file_size': 'total_size (gb)'})
    summary['total_size (gb)'] = round(summary['total_size (gb)'] / 1000, 2)

    print(summary.to_string())
    print()


def main(args):

    with open(args.conf, 'r') as f:
        conf = yaml.load(f)

    # Create directories
    slides_path = os.path.join(conf['data_path'], 'slides', 'svs')
    if not os.path.exists(slides_path):
        os.mkdir(slides_path)

    rnaseq_path = os.path.join(conf['data_path'], 'rnaseq')
    if not os.path.exists(rnaseq_path):
        os.mkdir(rnaseq_path)

    slides_df = pd.read_csv(os.path.join(conf['data_path'], 'slides_metadata.csv'), sep='|')
    rnaseq_df = pd.read_csv(os.path.join(conf['data_path'], 'rnaseq_metadata.csv'), sep='|')

    if args.in_both:
        slides_df = slides_df[slides_df['sample_id'].isin(rnaseq_df['sample_id'])]
        rnaseq_df = rnaseq_df[rnaseq_df['sample_id'].isin(slides_df['sample_id'])]
    
    print('Downloading slides...')
    print_summary(slides_df, 'experimental_strategy')

    api_download_iterative(slides_df, slides_path, multiprocess=args.multiprocess)
    print('OK')
    
    print('Downloading rnaseq...')
    print_summary(rnaseq_df, 'workflow_type')

    api_download_iterative(rnaseq_df, rnaseq_path, multiprocess=args.multiprocess)
    files = api_download_iterative(rnaseq_df, rnaseq_path, multiprocess=8)

    for file_name in files:
        zipped_file = os.path.join(rnaseq_path, file_name)
        unzipped_file = re.sub('\.gz$', '', zipped_file)
        gunzip(zipped_file, unzipped_file)
        os.remove(zipped_file)

    print('OK')


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Download Files")
    parser.add_argument('-conf', help="Path to config file", type=str, default='conf/user_conf.yaml')
    parser.add_argument('-in_both', help="Whether to download only files from samples with both slides and rnaseq", 
                        default=True)
    parser.add_argument('-multiprocess', help='Number of processes to run in parallel', default=4)

    args = parser.parse_args()

    main(args)