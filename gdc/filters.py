
FILTER_DICT = {'cases': {'program': 'project.program.name', 
                      'project_id': 'project.project_id', 
                      'primary_site': 'project.primary_site'},
                      
               'files': {'program': 'cases.project.program.name',
                         'project_id': 'cases.project.project_id',
                         'primary_site': 'cases.project.primary_site'}
              }

def _build_single_filter(key, value, endpoint):
            
    if type(value) == list:
        op = 'in'
    else:
        op = '='

    output_filter = {'op': op,
                     'content': {'field': FILTER_DICT[endpoint][key], 'value': value}}
                      
    return output_filter

def _build_slide_filter(experimental_strategies):

    op = 'in' if type(experimental_strategies) == list else '='

    slide_filter = {'op': 'and',
                    'content': [{'op': '=', 
                                    'content': {'field': 'data_type', 
                                                'value': 'Slide Image'}},
                                {'op': op,
                                    'content': {'field': 'experimental_strategy', 
                                                'value': experimental_strategies}}
                                ]
                    
                    }
    return slide_filter

def _build_rnaseq_filter(workflow_types):
    
    op = 'in' if type(workflow_types) == list else '='

    rnaseq_filter = {'op': 'and',
                     'content': [{'op': '=', 
                                  'content': {'field': 'experimental_strategy', 
                                              'value': 'RNA-Seq'}},
                                 {'op': op,
                                    'content': {'field': 'analysis.workflow_type', 
                                                'value': workflow_types}}
                                ]
                    
                    }

    return rnaseq_filter

def build_filter(cases_info, source, 
                 experimental_strategies=['Tissue Slide', 'Diagnostic Slide'], 
                 workflow_types=['HTSeq - Counts', 'HTSeq - FPKM-UQ', 'HTSeq - FPKM']):

    endpoint = 'cases' if source == 'cases' else 'files'

    if len(cases_info) == 1:
        output_filter = _build_single_filter(*list(cases_info.items())[0], endpoint)
    else:
        output_filter = {'op': 'and', 
                         'content': [_build_single_filter(k,v, endpoint) for k,v in cases_info.items()]}

    if source == 'slides':
    	output_filter = {'op': 'and', 'content': [_build_slide_filter(experimental_strategies), 
                                                  output_filter]}
    elif source == 'rnaseq':
        output_filter = {'op': 'and', 'content': [_build_rnaseq_filter(workflow_types), 
                                                  output_filter]}
        
    return output_filter
