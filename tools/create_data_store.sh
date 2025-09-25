#!/bin/sh
project_id="hiraoyogizzard"
data_store_id="sutra3"
curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
-H "X-Goog-User-Project: $project_id" \
"https://discoveryengine.googleapis.com/v1alpha/projects/$project_id/locations/global/collections/default_collection/dataStores?dataStoreId=$data_store_id" \
-d '{
  "displayName": "'"$data_store_id"'",
  "industryVertical": "GENERIC",
  "solutionTypes": ["SOLUTION_TYPE_SEARCH"]
}'
