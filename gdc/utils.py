import gzip
import shutil

def find_elem_by_submitter_id(elements, submitter_id):
    
    result = {}
    
    for elem in elements:
        if submitter_id == elem['submitter_id']:
            result = elem

    if result == {}:
        print('Warning: {} not found!'.format(submitter_id))

    return result
    
def gunzip(source_filepath, dest_filepath):
    with gzip.open(source_filepath, 'rb') as s_file:
        with open(dest_filepath, 'wb') as d_file:
            shutil.copyfileobj(s_file, d_file)