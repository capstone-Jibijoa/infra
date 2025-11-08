import pandas as pd
import json
import numpy as np
import glob
import os

# 이 파이썬 파일(script.py)의 실제 위치를 기준으로 절대 경로를 만듦
# 예: /.../infra/xlsx_to_json_pipeline/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# SCRIPT_DIR를 기준으로 data 폴더 경로를 설정
INPUT_PATTERN = os.path.join(SCRIPT_DIR, 'data/Quickpoll/qpoll*.xlsx')
INPUT_FILES = glob.glob(INPUT_PATTERN)

# SCRIPT_DIR를 기준으로 출력 폴더 경로를 설정
OUTPUT_JSON_DIR = os.path.join(SCRIPT_DIR, 'qpoll_json_output')

COLUMN_MAPPING = {
    '구분': 'category',
    '고유번호': 'panel_id',
    '성별': 'gender',
    '나이': 'age_raw',
    '지역': 'region',
    '설문일시': 'survey_timestamp'
}

def process_qpoll_file(path):
    """
    Processes a single qpoll-formatted Excel file into a structured DataFrame.
    [Final logic: Replaces '문항1' with '실제 질문 텍스트' in final output]
    """
    try:
        xlsx = pd.ExcelFile(path)

        # 1. Sheet 2를 읽어, 라벨 맵과 '질문 텍스트'를 순서대로 리스트에 저장
        df_labels = xlsx.parse(xlsx.sheet_names[1], header=None)
        
        # 라벨 맵과 질문 텍스트를 함께 저장할 리스트
        label_data_in_order = [] 
        row_index = 0

        while row_index < len(df_labels):
            # 1-1. '설문제목' 행 찾기 (ids 행)
            id_row_value = df_labels.iloc[row_index, 0] # A열
            if pd.isna(id_row_value):
                break
            if id_row_value.strip() != "설문제목":
                row_index += 1
                continue
            
            # 1-2. '설문제목' 행에서 ids 데이터(Series) 가져오기
            id_row_data_series = df_labels.iloc[row_index, 1:]
            
            # 1-3. '총참여자수' 위치 찾기
            stop_col_pos = None
            for i, item in enumerate(id_row_data_series):
                if pd.notna(item) and str(item).strip() == '총참여자수':
                    stop_col_pos = i 
                    break
            
            if stop_col_pos is not None:
                ids = id_row_data_series.iloc[:stop_col_pos].values
            else:
                ids = id_row_data_series.values
            
            # 1-4. 다음 행 (labels + 질문 텍스트 행)으로 이동
            row_index += 1
            if row_index >= len(df_labels):
                break
            
            # 1-5. A열에서 'key' (실제 질문 텍스트)를 읽음
            question_text = df_labels.iloc[row_index, 0]
            if pd.isna(question_text):
                question_text = "" # A열이 비어있을 경우
            question_text = question_text.strip()
            
            # 1-6. 'labels' 행 데이터(Series) 가져오기
            label_row_data_series = df_labels.iloc[row_index, 1:]
            
            if stop_col_pos is not None:
                labels = label_row_data_series.iloc[:stop_col_pos].values
            else:
                labels = label_row_data_series.values
            
            # 1-7. 라벨 맵 생성
            value_label_map = {
                str(id_).strip(): label
                for id_, label in zip(ids, labels)
                if pd.notna(id_) and pd.notna(label)
            }
            
            # 1-8. 라벨 맵과 질문 텍스트를 함께 리스트에 추가
            label_data_in_order.append({
                "text": question_text,
                "map": value_label_map
            })
            
            # 1-9. 다음 '설문제목' 블록으로 이동
            row_index += 1

        # 2. Sheet 1에서 데이터 읽기
        df_data = xlsx.parse(xlsx.sheet_names[0], header=1)

        # 3. '문항1'과 데이터를 매핑하는 딕셔너리 2개 생성
        
        # 3-1. G열부터 헤더(컬럼명)의 공백을 제거
        rename_map = {}
        for col_name in df_data.columns[6:]: # G열부터
            if pd.isna(col_name):
                continue
            stripped_name = str(col_name).strip()
            if col_name != stripped_name:
                rename_map[col_name] = stripped_name
        
        if rename_map:
            print(f"Normalizing {len(rename_map)} column headers...")
            df_data.rename(columns=rename_map, inplace=True)
            
        # 3-2. G열(인덱스 6)부터의 '문항' 컬럼 이름을 리스트로 가져옴
        question_cols = list(df_data.columns[6:]) 
        
        if not question_cols:
            print(f"Warning: No question columns (G onwards) found in {path}")
            return pd.DataFrame()
            
        # 3-3. 2개의 딕셔너리를 생성
        all_label_maps = {}    # "문항1" -> {라벨 맵} (라벨 변환용)
        question_text_map = {} # "문항1" -> "실제 질문 텍스트" (교체용)
        
        for i, col_name in enumerate(question_cols):
            if i < len(label_data_in_order):
                data_blob = label_data_in_order[i]
                all_label_maps[col_name] = data_blob['map']
                question_text_map[col_name] = data_blob['text']
            else:
                print(f"Warning: No label data found for column '{col_name}' (index {i})")
                all_label_maps[col_name] = {}
                question_text_map[col_name] = col_name # 기본값으로 '문항1' 사용

        # 4. Wide to Long (melt)
        id_vars = list(df_data.columns[:6])
        df_melted = df_data.melt(
            id_vars=id_vars,
            value_vars=question_cols,
            var_name='survey_question',    # "문항1", "문항2"가 이 컬럼으로
            value_name='survey_answers_raw'
        )

        # 5. 라벨 적용 함수 정
        def apply_labels_from_map(row):
            question_key = str(row['survey_question']).strip() 
            raw_value = row['survey_answers_raw']
            value_label_map = all_label_maps.get(question_key) # 3-3에서 만든 맵
            
            if value_label_map is None:
                return [f"Map not found for '{question_key}'"] if pd.notna(raw_value) else []
            if pd.isna(raw_value):
                return []
            
            id_string = str(raw_value)
            labeled_answers = []
            ids = id_string.split(',')
            
            for id_val in ids:
                id_val = id_val.strip()
                if not id_val:
                    continue
                try:
                    num_id = int(float(id_val)) 
                    key = f"보기{num_id}" 
                    labeled_answers.append(value_label_map.get(key, f"Unknown ID: {key}"))
                except (ValueError, TypeError):
                    continue
            return labeled_answers

        # 6. 라벨 적용
        df_melted['survey_answers'] = df_melted.apply(apply_labels_from_map, axis=1)

        # 7. [신규] 'survey_question' 컬럼의 값을 "문항1" -> "실제 질문 텍스트"로 교체
        df_melted['survey_question'] = df_melted['survey_question'].map(question_text_map).fillna(df_melted['survey_question'])

        # 8. [수정] 컬럼 정리 (기존 7번)
        df_melted.drop(columns=['survey_answers_raw'], inplace=True)
        df_melted.rename(columns=COLUMN_MAPPING, inplace=True)

        # 9. [수정] NaN 값 정리 후 반환 (기존 8번)
        return df_melted.replace({np.nan: None})

    except Exception as e:
        print(f"Error processing file {path}: {e}")
        raise

# --- Main Execution ---
if __name__ == '__main__':
    
    # JSON을 저장할 폴더 생성 (이미 있으면 넘어감)
    os.makedirs(OUTPUT_JSON_DIR, exist_ok=True)
    
    total_files_processed = 0
    
    try:
        all_files = INPUT_FILES
        if not all_files:
            print("No 'qpoll*.xlsx' files found in 'data/Quickpoll/'.")
        
        for file_path in all_files:
            print(f"--- Processing {file_path} ---")
            
            # 파일 루프가 돌 때마다 집계 딕셔너리를 새로 만듦
            all_data_by_panel = {} 
            
            processed_df = process_qpoll_file(file_path)
            
            if processed_df.empty:
                print(f"Skipping empty processed data from {file_path}.")
                continue
            
            for col in processed_df.select_dtypes(include=['datetime64[ns]']).columns:
                processed_df[col] = processed_df[col].dt.strftime('%Y-%m-%dT%H:%M:%S')

            for record in processed_df.to_dict('records'):
                panel_id = record.get('panel_id')
                if not panel_id:
                    continue

                if panel_id not in all_data_by_panel:
                    all_data_by_panel[panel_id] = {
                        'panel_id': panel_id,
                        'category': record.get('category'),
                        'gender': record.get('gender'),
                        'age_raw': record.get('age_raw'),
                        'region': record.get('region'),
                        'surveys': []
                    }
                
                survey_data = {
                    'survey_question': record.get('survey_question'),
                    'survey_answers': record.get('survey_answers'),
                    'survey_timestamp': record.get('survey_timestamp')
                }
                all_data_by_panel[panel_id]['surveys'].append(survey_data)

            # 이 파일의 데이터 집계가 끝나면
            final_records = list(all_data_by_panel.values())
            
            if not final_records:
                print("No data to save for this file.")
                continue

            # 이 파일만의 JSON 파일 경로를 생성
            # 예: 'data/Quickpoll/qpoll_A.xlsx' -> 'qpoll_A.json'
            base_name = os.path.basename(file_path) # 'qpoll_A.xlsx'
            file_name_without_ext, _ = os.path.splitext(base_name) # 'qpoll_A'
            output_json_path = os.path.join(OUTPUT_JSON_DIR, f"{file_name_without_ext}.json")
            
            # 이 파일의 데이터를 JSON으로 즉시 저장
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(final_records, f, ensure_ascii=False, indent=4)
            
            print(f"Successfully processed {len(final_records)} users.")
            print(f"Data saved to '{output_json_path}'\n")
            total_files_processed += 1

        print(f"\n--- Execution Finished ---")
        print(f"Total files processed: {total_files_processed}")

    except Exception as e:
        print(f"\n--- An error occurred during execution ---")
        print(f"Failed to process files: {e}")