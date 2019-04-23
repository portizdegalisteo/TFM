import requests
import io
import json
import pandas as pd
from gdc.filters import build_filter
from gdc.utils import find_elem_by_submitter_id


CASES_ENDPOINT = 'https://api.gdc.cancer.gov/cases'
FILES_ENDPOINT = 'https://api.gdc.cancer.gov/files'

SOURCE_PREFIXES = {'files': '',
                   'samples': 'cases.samples.',
                   'portions': 'cases.samples.portions.',
                   'slides': 'cases.samples.portions.slides.'}

def _multiple_column_check(df):
    multiple_check = [x for x in df.columns if '.1.' in x]
    if len(multiple_check) > 0:
        print('WARNING! Multiple instances found in fields: ', multiple_check)


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


def _process_slide_json(file_json, fields):
    
    # Files data
    file_data = {k: file_json.get(k) for k in fields['files']}

    file_data['file_id'] = file_json['file_id']
    file_data['slide_id'] = file_json['submitter_id'].replace('_slide_image', '')
    file_data['case_id'] = file_json['submitter_id'][:12]
    file_data['sample_id'] = file_json['submitter_id'][:16]

    if 'file_size' in file_data:
        file_data['file_size'] = round(file_data['file_size'] / 10**6, 2)
    
    # Cases
    if len(file_json['cases']) > 1:
        case_json = find_elem_by_submitter_id(file_json['cases'], submitter_id=file_data['case_id'])
    else:
        case_json = file_json['cases'][0]
    case_data = {k: case_json.get(k) for k in fields['cases']}
    
    # Samples
    if len(case_json['samples']) > 1:
        sample_json = find_elem_by_submitter_id(case_json['samples'], submitter_id=file_data['sample_id'])
    else:
        sample_json = case_json['samples'][0]
    sample_data = {k: sample_json.get(k) for k in fields['samples']}

    # Slides
    slide_json = _find_slide(sample_json['portions'], file_data['slide_id'])
    slide_data = {k: slide_json.get(k) for k in fields['slides']}
    
    # All
    all_data = {**file_data, **case_data, **sample_data, **slide_data}
    
    return all_data

def get_cases(filter, fields, max_results=10000):

    # Build query
    query_fields = ['submitter_id'] + fields['cases']
    for source, source_fields in fields.items():
        if source != 'cases':
            query_fields += [source + '.' + x for x in source_fields]

    query_filter = build_filter(filter, source='cases')

    params = {'fields': ','.join(query_fields),
              'filters': query_filter, 
              'format': 'TSV',
              'size': max_results}

    # Run query
    response = requests.post(CASES_ENDPOINT, headers={'Content-Type': 'application/json'}, json=params)

    # Build DF
    cases_df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), sep='\t')

    _multiple_column_check(cases_df)

    # Reorganise columns
    cases_df.columns = [x.replace('.0', '') for x in cases_df.columns]
    cases_df = cases_df[query_fields]

    cases_df.rename(columns={'submitter_id': 'case_id'}, inplace=True)
    cases_df.rename(columns={'project.program.name': 'program_name'}, inplace=True)

    cases_df.columns = [x.rsplit('.')[-1] for x in cases_df.columns]
    
    return cases_df


def get_rnaseq_metadata(filter, fields, max_results=10000, 
                        workflow_types=['HTSeq - Counts', 'HTSeq - FPKM-UQ', 'HTSeq - FPKM']):

    # Build query
    id_fields = ['file_id', 'cases.submitter_id', 'cases.samples.submitter_id', 'submitter_id']
    query_fields = [SOURCE_PREFIXES.get(s, s + '.') + f for s,fs in fields.items() for f in fs]
    query_fields = id_fields + query_fields

    query_filter = build_filter(filter, source='rnaseq', workflow_types=workflow_types)

    params = {'fields': ','.join(query_fields),
              'filters': query_filter, 
              'format': 'TSV',
              'size': max_results}

    # Run query
    response = requests.post(FILES_ENDPOINT, headers={'Content-Type': 'application/json'}, json=params)

    # Build DF
    rnaseq_df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), sep='\t')

    _multiple_column_check(rnaseq_df)

    # Reorganise columns
    rnaseq_df.columns = [x.replace('.0', '') for x in rnaseq_df.columns]
    rnaseq_df = rnaseq_df[query_fields]

    rnaseq_df.rename(columns={'submitter_id': 'rnaseq_id', 
                              'cases.submitter_id': 'case_id',
                              'cases.samples.submitter_id': 'sample_id'}, inplace=True)

    rnaseq_df.columns = [x.rsplit('.')[-1] for x in rnaseq_df.columns]

    # File size to MB
    if 'file_size' in rnaseq_df.columns:
        rnaseq_df['file_size'] = round(rnaseq_df['file_size'] / 10**6, 2)

    # Create filename (sample_id + workflow_type + '.txt.gz')
    rnaseq_df['file_name'] = rnaseq_df.apply(lambda x: 
                                             x['sample_id'] + '_' + x['workflow_type'].replace(' ', '') + '.txt.gz', 
                                             axis=1)

    return rnaseq_df


def get_slides_metadata(filter, fields, max_results=10000,
                        experimental_strategies=['Tissue Slide', 'Diagnostic Slide']):

    # Build query
    id_fields = ['file_id', 'submitter_id', 'cases.submitter_id', 'cases.samples.submitter_id', 
                 'cases.samples.portions.submitter_id', 'cases.samples.portions.slides.submitter_id']

    query_fields = [SOURCE_PREFIXES.get(s, s + '.') + f for s,fs in fields.items() for f in fs]
    query_fields = id_fields + query_fields

    query_filter = build_filter(filter, source='slides', experimental_strategies=experimental_strategies)

    params = {'fields': ','.join(query_fields),
              'filters': query_filter, 
              'format': 'JSON',
              'size': max_results}

    # Run query
    response_json = requests.post(FILES_ENDPOINT, headers={'Content-Type': 'application/json'}, json=params)
    response_json = json.loads(response_json.content)

    # Process output
    slides_data = []

    for hit in response_json['data']['hits']:
        slide_data = _process_slide_json(hit, fields)
        slides_data.append(slide_data)

    slides_df = pd.DataFrame(slides_data)

    # Reorganise columns
    id_columns = ['file_id', 'case_id', 'sample_id', 'slide_id']
    columns = id_columns + [f for s,fs in fields.items() for f in fs]

    slides_df = slides_df[columns]
    slides_df['file_name'] = slides_df.apply(lambda x: x['slide_id'] + '.' + x['data_format'].lower(), axis=1)

    return slides_df