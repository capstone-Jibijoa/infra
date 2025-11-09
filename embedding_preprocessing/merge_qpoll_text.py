import os
import json
import glob
import re

# --- 1. 경로 설정 ---
# 이 스크립트 파일(merge_qpoll_data.py)의 위치를 기준으로 경로를 설정합니다.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 이 스크립트의 상위 폴더(PROJECT_ROOT)를 찾습니다. (예: /.../infra/)
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# [입력] qpoll 문장 파일이 있는 폴더
QPOLL_INPUT_DIR = os.path.join(
    PROJECT_ROOT,
    'embedding_preprocessing', # 'json_to_text.py' 스크립트가 있던 폴더
    'sentence_output_by_qpoll_topic' # qpoll 결과 폴더
)

# [출력] 최종 마스터 qpoll 파일 경로
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'merged_sentence_output_by_qpoll_topic')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'merged_qpoll_text.json')

def load_json(path):
    """JSON 파일을 안전하게 로드"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"  > 파일 로드 오류: {os.path.basename(path)}, {e}")
        return None

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # 모든 qpoll 답변 객체를 저장할 마스터 리스트
    master_data = []
    
    # --- Qpoll 데이터 병합 ---
    qpoll_files = glob.glob(os.path.join(QPOLL_INPUT_DIR, '*.json'))
    if not qpoll_files:
        print(f"오류: '{QPOLL_INPUT_DIR}' 폴더에서 *.json 파일을 찾을 수 없습니다.")
        return

    print(f"--- Qpoll 데이터 병합 시작 (총 {len(qpoll_files)}개 파일) ---")
    
    total_qpoll_sentences = 0
    for file_path in qpoll_files:
        data = load_json(file_path)
        
        # 파일 형식 확인
        if data is None or "topic_file_id" not in data or "generated_data" not in data:
            print(f"  > 건너뛰기: {os.path.basename(file_path)} (형식 오류)")
            continue
            
        # topic_id = data["topic_file_id"]
        generated_data = data["generated_data"]
        
        # 'generated_data' 리스트를 순회
        for item in generated_data:
            sentence = item.get("sentence_for_embedding")
            
            # [중요] 문장이 null(None)이거나 빈 문자열인 경우는 제외
            if sentence: 
                master_data.append({
                    "panel_id": item.get("panel_id"),
                    #" topic_id": topic_id,
                    "question": item.get("original_question", "N/A"),
                    "sentence": sentence
                })
                total_qpoll_sentences += 1
                
    print(f"--- Qpoll 문장 {total_qpoll_sentences}개 병합 완료 ---")

    # --- 최종 마스터 파일 저장 ---
    if not master_data:
        print("\n병합할 데이터가 없습니다.")
        return

    print(f"\n--- 최종 파일 저장 중 ---")
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=4)
        
        print(f"성공! 총 {len(master_data)}개의 문장이 '{OUTPUT_FILE}'에 저장되었습니다.")
        
        if master_data:
            print("\n--- 최종 데이터 구조 예시 ---")
            print(json.dumps(master_data[0], indent=4, ensure_ascii=False))

    except Exception as e:
        print(f"최종 파일 저장 오류: {e}")

if __name__ == '__main__':
    main()