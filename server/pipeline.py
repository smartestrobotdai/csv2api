import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import os

def apply_pipeline(pipeline, base_dir):
  df = None
  step = pipeline[0]
  
  source = os.path.join(base_dir, step['source'])
  
  # check if source exists
  if not os.path.isfile(source):
    raise Exception(f"File not found: {source}")

  
  # delimiter is optional
  delimiter = step.get('delimiter', None)
  skiprows = step.get('skiprows', None)
  df = pd.read_csv(source, header=0, skiprows=skiprows, low_memory=False, delimiter=delimiter)  
  
  # Apply steps
  for step in pipeline:
    action = step['action']
    if action == 'truncate':
      df = df[:step['nrows']]
    elif action == 'sample':
      nrows = step.get('nrows', 0)
      if nrows < len(df):
        df = df.sample(n=step['nrows'])
    elif action == 'select_columns':
      df = df[step['columns']]
    elif action == 'rename_columns':
      df.rename(columns=step['rename_map'], inplace=True)
    
    elif action == 'pca_transform':
      pca_col = step['column']
      list_of_arrays = df[pca_col].apply(lambda x: np.fromstring(x.strip('[]'), sep=' ')).tolist()
      array_2d = np.array(list_of_arrays)
      pca = PCA(n_components=step['n_components'])
      components = pca.fit_transform(array_2d)
      df[pca_col] = components.tolist()
    elif action == 'conditions':
      print('conditions', step['conditions'])
      condition_list = []
      for condition in step['conditions']:
        col = condition['column']
        operator = condition['operator']
        value = condition['value']
        if operator == "==":
          if value == 'null':
            condition_list.append(df[col].isnull())
          else:
            condition_list.append(df[col] == value)
        elif operator == "<":
          condition_list.append(df[col] < value)
        elif operator == ">":
          condition_list.append(df[col] > value)
        elif operator == "!=":
          if value == 'null':
            condition_list.append(df[col].notnull())
          else:
            condition_list.append(df[col] > value)
        elif operator == "contains":
          condition_list.append(df[col].astype(str).str.contains(value))
        

      if len(condition_list) > 0:
        print('condition_list', condition_list)
        # add more operators as needed
        if 'condition_logic' in step and step['condition_logic'] == 'and':
          final_condition = np.logical_and.reduce(condition_list)
        else:
          final_condition = np.logical_or.reduce(condition_list)
        
        df = df[final_condition]
    elif action == 'remove_duplicates':
      columns = step['columns']
      df.drop_duplicates(inplace=True, subset=columns)
    elif action == 'append':
      # get current time
      print('append', step['values'])
      cols = df.columns[:-1].tolist()
      values = step['values']
      row = {col: [val] for col, val in zip(cols, values)}
      row['create_at'] = [pd.Timestamp.now()]
      row = pd.DataFrame(row)
      print(row)
      row.to_csv(source, mode='a', header=False, index=False)
      df = row
    
  return df