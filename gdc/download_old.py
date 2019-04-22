import os
import re
import json
import subprocess
import requests
import tarfile
from functools import partial
from multiprocessing import Pool
import pandas as pd
try:
    get_ipython()
    from tqdm import tqdm_notebook as tqdm
except:
    from tqdm import tqdm

DATA_ENDPOINT = 'https://api.gdc.cancer.gov/data/'

def gdc_tool_download(files, out_dir, gdc_tool):
    
    if isinstance(files, pd.DataFrame):
        files = files['file_id'].tolist()
    files = ' '.join(files)
    
    command_template = "{} download -d '{{out_dir}}' {{files}}".format(gdc_tool)
    try:
        output = subprocess.check_output(command_template.format(out_dir=out_dir, files=files), 
                                         shell=True).decode('utf-8')
        
        print(output)
    
    except subprocess.CalledProcessError as e:
        print(e.output.decode('utf-8'))


def _save_response(response, output_dir, stream=True, file_size=None, chunk_size=1, 
                   file_name=None, progress_bar=True):
    
    response_head_cd = response.headers["Content-Disposition"]
    file_name = file_name if file_name != None else re.findall("filename=(.+)", response_head_cd)[0]
    file_path = os.path.join(output_dir, file_name)
    
    output_file = open(file_path, "wb")
        
    if stream:        

        if progress_bar:

            # This line is the strange hack
            print(' ', end='', flush=True)

            n_chunks = int(round(file_size*1024/chunk_size, 0))                
            progress_bar =  tqdm(leave=False, total=n_chunks, desc=file_name, 
                                unit='⋅{}kb'.format(chunk_size), unit_scale=True)

            for chunk in response.iter_content(chunk_size= int(chunk_size*1024)):
                output_file.write(chunk)
                progress_bar.update(1)
            
            if progress_bar.n < n_chunks:
                progress_bar.update(n_chunks - progress_bar.n)
            progress_bar.close()
        
        else:          

            for chunk in response.iter_content(chunk_size= int(chunk_size*1024)):
                output_file.write(chunk)


    else:
        output_file.write(response.content)

    output_file.close()
    
    return file_name
    
    
def api_download_single(file, output_dir, stream=True, chunk_size=1, progress_bar=True):
    
    query = DATA_ENDPOINT + file['file_id']
        
    response = requests.get(query, 
                            headers = {"Content-Type": "application/json"}, 
                            stream=stream)
    
    file_name = file['file_name'] if 'file_name' in file else None
    file_name = _save_response(response, output_dir, stream, 
                              file['file_size'], chunk_size, file_name, progress_bar)
    
    return file_name



def api_download_iterative(files, output_dir, stream=True, chunk_size=1, multiprocess=False):
    
    if isinstance(files, pd.DataFrame):
        files = files.to_dict(orient='rows')
    
    progress_bar = partial(tqdm, desc='Files', unit='file', unit_scale=True)
    
    results = []
    
    if not multiprocess:
        for file in progress_bar(files):
            res = api_download_single(file, output_dir, stream=stream, chunk_size=chunk_size)
            results.append(res)
    else: 
        func = partial(api_download_single, output_dir=output_dir, stream=stream, 
                       chunk_size=chunk_size, progress_bar=True)

        with Pool(processes=multiprocess) as pool:
            for res in progress_bar(pool.imap_unordered(func, files), total=len(files)):
                results.append(res)
            
    return results
        
        
def api_download_batch(files, output_dir, stream=True, chunk_size=1):
    
    if isinstance(files, pd.DataFrame):
        file_ids = files['file_id'].tolist()
        total_size = files['file_size'].sum()
    else:
        file_ids = [x['file_id'] for x in files]
        total_size = sum(x['file_size'] for x in files)
    
    estimated_compressed_size = max(total_size / 1.3, 5)
        
    params = {"ids": file_ids}
    response = requests.post(DATA_ENDPOINT, 
                             data = json.dumps(params), 
                             headers = {"Content-Type": "application/json"}, 
                             stream=stream)
    
    file_name = _save_response(response, output_dir, stream, estimated_compressed_size, chunk_size)
    
    # Untar
    tf = tarfile.open(os.path.join(output_dir, file_name))
    tf.extractall(path=output_dir)
    
    # Remove files
    os.remove(os.path.join(output_dir, file_name))
    os.remove(os.path.join(output_dir, 'MANIFEST.TXT'))
    
    return response