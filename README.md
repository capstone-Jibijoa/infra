# infra
AWS Infra &amp; DB

## 목차
1. [xlsx to json pipeline 사용 가이드](#1-xlsx-to-json-pipeline-사용-가이드)

# 1. xlsx to json pipeline 사용 가이드
## 경로

``` shell
xlsx_to_json_pipeline/
├── data/
│   ├── Quickpoll/qpoll 엑셀 파일 위치
│   └── Welcome/welcome 엑셀 파일 위치
├── convert_qpoll_to_json.py
├── convert_qpolls_to_merged_json.py
├── convert_welcome_to_json.py
└── merge_welcome_and_qpoll.py
```
## 각 파일의 변환 역할
json으로 변환된 모든 파일은 ./xlsx/json_output 폴더에 저장됩니다.
### Welcome
상위 두 개 객체가 빈 값이므로, 지우고 사용해야 합니다.

[convert_welcome_to_json.py](./xlsx_to_json_pipeline/convert_welcome_to_json.py) : Welcome1, 2 -> welcome_data.json
### Qpoll

[convert_qpoll_to_json.py](./xlsx_to_json_pipeline/convert_qpoll_to_json.py) : qpoll.xlsx files -> *qpoll.json files*

[convert_qpolls_to_merged_json.py](./xlsx_to_json_pipeline/convert_qpolls_to_merged_json.py) : qpoll files -> merged_qpoll_data.json
### merge(현재 사용하지 않음)
[merge_welcome_and_qpoll.py](./xlsx_to_json_pipeline/merge_welcome_and_qpoll.py) : merged_data.json + qpoll_data.json -> final_data.json

