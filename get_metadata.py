import yaml
import os
import argparse

from gdc.metadata import get_rnaseq_metadata
from gdc.metadata import get_slides_metadata
from gdc.metadata import get_cases

def main(args):

    with open(args.conf, 'r') as f:
        conf = yaml.load(f)

    cases_df = get_cases(conf['cases_info'], conf['fields']['cases'])
    cases_df.to_csv(os.path.join(conf['data_path'], 'cases.csv'), sep='|', index=False)

    slides_df = get_slides_metadata(conf['cases_info'], conf['fields']['slides'])
    slides_df.to_csv(os.path.join(conf['data_path'], 'slides_metadata.csv'), sep='|', index=False)

    rnaseq_df = get_rnaseq_metadata(conf['cases_info'], conf['fields']['rnaseq'])
    rnaseq_df.to_csv(os.path.join(conf['data_path'], 'rnaseq_metadata.csv'), sep='|', index=False)

if __name__ == "__main__":

    parser = argparse.ArgumentParser("Download Files")
    parser.add_argument('-conf', help="Path to config file", type=str, default='conf/user_conf.yaml')

    args = parser.parse_args()

    main(args)