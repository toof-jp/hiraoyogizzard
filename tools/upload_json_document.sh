#!/bin/sh
curl -X POST \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
"https://discoveryengine.googleapis.com/v1beta/projects/hiraoyogizzard/locations/global/collections/default_collection/dataStores/mystore/branches/0/documents?documentId=hoge2" \
-d '{
  "jsonData": "{ \"title\": \"test title\", \"categories\": [\"cat_1\", \"cat_2\"], \"uri\": \"test uri\", \"content\": \"『法の智慧に従う』とは、感覚と認識の領域を観察し、根源的に究明すること、因果応報を観察すること、
                              阿羅漢の眼を観察すること、心が自由であることの幸福と、瞑想の幸福を観察すること、阿羅漢、縁覚、
                              及び力ある菩薩の超自然的な力を観察することです。\"}"
}'
