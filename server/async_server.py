from aiohttp import web
import json
import logging
import os
import pandas as pd
import gzip
import io
import getopt
import sys
from sklearn.decomposition import PCA

from pipeline import apply_pipeline

app = web.Application(client_max_size = 1024 * 1024 * 100)

file_base_dir = '../files'

def badRequest(web, msg, status):
  ret_obj = {"error": {"code": status, "message": f"invalid request format: {msg}"}}
  return web.json_response(ret_obj, status=status)


def get_output_params(request):
  output_orient = request.query.get('output_orient', 'records')
  output_index = request.query.get('output_index', True)
  return output_orient, output_index

def get_columns(request):
  columns = request.query.get('columns', '')
  columns = [] if columns == '' else columns.split(',')
  return columns

def get_json_file(request, path):
  startpos = int(request.query.get('startpos', 0))
  nrows = int(request.query.get('nrows', 0))
  columns = get_columns(request)
  output_orient, output_index = get_output_params(request)
  condition = request.query.get('condition', '')
  print('get json, query', request.query)
  try:
    df = pd.read_json(path)
    if condition:
      print('condition:', condition)
      df = df[df.eval(condition)]
    if startpos > 0:
      df = df.iloc[startpos:]
    if nrows > 0:
      df = df.iloc[:nrows]
    if len(columns) > 0:
      df = df[columns]
    print('ready to send', df)
    res_json = df.to_json(orient=output_orient, index=output_index) # type: ignore
    return web.Response(text=res_json)
  
  except FileNotFoundError:
    return badRequest(web, f"File not found", 400)
  except Exception as e:
    return badRequest(web, f"An error occurred: {str(e)}", 400)


def get_csv_file(request, path):
  nrows = int(request.query.get('nrows', 0))
  skiprows = int(request.query.get('skiprows', 0))
  startpos = int(request.query.get('startpos', 0))
  delimiter = request.query.get('delimiter', ',')
  columns = get_columns(request)
  output_orient, output_index = get_output_params(request)
  pca = request.query.get('pca', 0)
  index_col = request.query.get('index_col', None)
  condition = request.query.get('condition', '')
  if nrows == 0:
    nrows = None

  
  try:
    df = pd.read_csv(path, header=0, skiprows=lambda x: x != 0 and x < startpos+1, 
              nrows=nrows, low_memory=False, 
              delimiter=delimiter, index_col=index_col)
    if len(columns) > 0:
      df = df[columns]

    if condition:
      df = df[df.eval(condition)]
      
    if int(pca) == 1:
      pca = PCA(n_components=3)
      data = df.values
      components = pca.fit_transform(data)

      df_new = pd.DataFrame(components)
      if index_col is not None:
        df_new.index = df.index
      df = df_new
      
    res_json = df.to_json(orient=output_orient, index=output_index) # type: ignore
    return web.Response(text=res_json)
  except FileNotFoundError:
    return badRequest(web, f"File not found", 404)
  except Exception as e:
    return badRequest(web, f"An error occurred: {str(e)}", 400)
  
# test:
# curl -X POST -H "Content-Type: application/json" -d @test/test1.json http://localhost:9191/api/v1/fetchData
async def fetchData(request):
  # get the json file from the request
  try:
    data = await request.json()
    print('data', data)
    pipeline = data['steps']
    print('steps', pipeline)
    base_dir = '../../files'
    transformed_df = apply_pipeline(pipeline, base_dir)
    res_json = transformed_df.to_json(orient='records', index=True)
    return web.Response(text=res_json)
  except Exception as e:
    return badRequest(web, f"An error occurred: {str(e)}", 400)

# curl -F "file=@test3.csv" http://192.168.2.1:9191/api/v1/csv/upload
# gzip -c test3_big.csv | curl -X POST  -H "Content-Type: multipart/form-data" -F "file=@-;filename=test3_big.csv.gz" http://192.168.2.1:9191/api/v1/csv/test3_big/upload
# curl -X POST  -H "Content-Type: multipart/form-data" -F "file=@test3_big.csv" http://192.168.2.1:9191/api/v1/csv/upload
async def handle_file_upload(request):
  reader = await request.multipart()
  field = await reader.next()
  assert field.name == 'file'
  print(field)
  filename = field.filename
  size = 0
  
  data = await field.read()  # Read the file data directly from the request payload
  if filename.endswith('.gz'):  # If the file is a gzip file
    with gzip.open(io.BytesIO(data), 'rb') as f_in:  # Decompress the file data
        decompressed_data = f_in.read()
        filename = filename[:-3]  # Remove .gz from filename
  elif filename.endswith('.csv'):
    decompressed_data = data  # If the file is not a gzip file, use the original data
  else:
    return web.Response(text=f'only .csv or .csv.gz files are supported')
  
  size = len(decompressed_data)
  with open(os.path.join('../csv_files', filename), 'wb') as f_out:  # Save the file
    f_out.write(decompressed_data) # type: ignore
  
  return web.Response(text=f'Successfully saved file {filename} Size: {size} bytes')

def main(argv):
  host = '0.0.0.0'
  port = 9191
  print('starting server')
  with open('config.json', 'r') as f:
    config = json.load(f)
    host = config['host']
    port = int(config['port'])
  print('configration loaded', config)
  opts, args = getopt.getopt(argv,"",["ip=", "host="])
  
  for opt, arg in opts:
    if opt in ("--host"):
      host = arg
    if opt in ("--port"):
      port = int(arg)

  app.add_routes([web.post('/api/v1/fetchData', fetchData),
                  web.post('/api/v1/csv/upload', handle_file_upload)])
  web.run_app(app, port=port, host=host)
    
if __name__ == '__main__':
  main(sys.argv[1:])
# curl "http://localhost:9191/api/v1/csv/test2?nrows=10&startpos=0&columns=Id,Name&delimiter=%20"
