from gdc.utils import find_elem_by_submitter_id

def _find_slide(portions, slide_id):

    for portion in portions:
        for slide in portion['slides']:
            if slide_id == slide['submitter_id']:
                slide_json = slide
                break
        else:
            # Continue if the inner loop wasn't broken.
            continue
        # Inner loop was broken, break the outer.
        break

    return slide_json

def _get_file_data(file_json, fields):
    
    file_data = {k: file_json.get(k) for k in fields}

    file_data['file_id'] = file_json['file_id']
    file_data['slide_id'] = file_json['submitter_id'].replace('_slide_image', '')
    file_data['case_id'] = file_json['submitter_id'][:12]
    file_data['sample_id'] = file_json['submitter_id'][:16]

    if 'file_size' in file_data:
        file_data['file_size'] = round(file_data['file_size'] / 10**6, 2)
    
    return file_data

def get_single_slide_data(file_json, fields_conf):
    
    # Files data
    file_data = _get_file_data(file_json, fields_conf['files'])
    
    # Cases
    case_json = find_elem_by_submitter_id(file_json['cases'], submitter_id=file_data['case_id'])
    case_data = {k: case_json.get(k) for k in fields_conf['cases']}
    
    # Samples
    sample_json = find_elem_by_submitter_id(case_json['samples'], submitter_id=file_data['sample_id'])
    sample_data = {k: sample_json.get(k) for k in fields_conf['samples']}

    # Slides
    slide_json = _find_slide(sample_json['portions'], file_data['slide_id'])
    slide_data = {k: slide_json.get(k) for k in fields_conf['slides']}
    
    # All
    full_data = {**file_data, **case_data, **sample_data, **slide_data}
    
    return full_data    