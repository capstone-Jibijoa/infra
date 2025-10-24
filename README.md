# infra
AWS Infra &amp; DB

## 목차
1. [xlsx to json pipeline 사용 가이드](#1-xlsx-to-json-pipeline-사용-가이드)

## 1. xlsx to json pipeline 사용 가이드
[convert_welcome_to_json.py](./xlsx_to_json_pipeline/convert_welcome_to_json.py) : Welcome1, 2 -> welcome_data.json

[convert_qpoll_to_json.py](./xlsx_to_json_pipeline/convert_qpoll_to_json.py) : qpoll files -> qpoll_data.json

[merge_welcome_and_qpoll.py](./xlsx_to_json_pipeline/merge_welcome_and_qpoll.py) : merged_data.json + qpoll_data.json -> final_data.json

