# csv2api

To convert a CSV file into RESTAPI with a json format config file
config example:
{
  "steps": [
    {
      "action": "select_columns",
      "columns": ["col1", "col3", "col5"]
    },
    {
      "action": "rename_columns",
      "rename_map": {
        "col1": "new_col1",
        "col3": "new_col3"
      }
    },
    {
      "action": "pca_transform",
      "pca_column": "vector"
      "n_components": 3
    },
    {
      "action": "remove_duplicates"
    },
    {
      "action": "conditions",
      "conditions": [
        {
          "column": "Id",
          "operator": "contains",
          "value": "A"
        },
        {
          "column": "Name",
          "operator": "contains",
          "value": "B"
        }
      ],
      "condition_logic": "and"
    }
  ]
}

Put your csv file into the folder: ./files, then 
./rebuild.sh

You could test it with 
curl -X POST -H "Content-Type: application/json" -d @test/test1.json http://localhost:9191/api/v1/fetchData

