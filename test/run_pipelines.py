import json
import argparse
from server.pipeline import apply_pipeline


if __name__ == "__main__":
  # Initialize argparse
  parser = argparse.ArgumentParser(description='Apply a data transformation pipeline to a CSV file.')
  parser.add_argument('json_file', type=str, help='Path to the JSON file describing the pipeline.')

  # Parse arguments
  args = parser.parse_args()
  
  json_file = args.json_file

  # Apply pipeline
  with open(json_file, 'r') as f:
    pipeline = json.load(f)['steps']
  transformed_df = apply_pipeline(pipeline, '../files')
  print(transformed_df)

