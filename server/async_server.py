from aiohttp import web
import json
import logging
import os
import pandas as pd
import gzip
import io

app = web.Application(client_max_size = 1024 * 1024 * 100)

def badRequest(web, msg, status):
  ret_obj = {"error": {"code": status, "message": f"invalid request format: {msg}"}}
  return web.json_response(ret_obj, status=status)

async def getCSV(request):
  print(request.query)
  nrows = int(request.query.get('nrows', 0))
  skiprows = int(request.query.get('skiprows', 0))
  delimiter = request.query.get('delimiter', ',')
  
  object_id = request.match_info['id']
  path = os.path.join('../csv_files', f'{object_id}.csv')
  if nrows > 0:
    df = pd.read_csv(path, skiprows=skiprows, nrows=nrows, low_memory=False, delimiter=delimiter)
  else:
    df = pd.read_csv(path, skiprows=skiprows, low_memory=False, delimiter=delimiter)
    
  res_json = df.to_json(orient = 'records')
  return web.json_response(res_json)

# curl -H "Content-Encoding: gzip" -F "file=@test2.csv" http://192.168.2.1:9191/api/v1/csv/test2/upload
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

with open('config.json', 'r') as f:
  config = json.load(f)
  app.add_routes([web.get('/api/v1/csv/{id}', getCSV),
                  web.post('/api/v1/csv/upload', handle_file_upload)])
  
  if __name__ == '__main__':
    web.run_app(app, port=config['port'], host=config['listen-ip'])
# curl "http://192.168.2.1:9191/api/v1/csv/sp500_stocks?nrows=10&skiprows=10"
