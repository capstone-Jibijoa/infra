import os
import json
import glob

# --- 1. 경로 설정 ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # .../infra/embedding

# [입력] 나눠진 임베딩 파일들 (이름 패턴)
# 'qpoll_embedding1.json', 'qpoll_embedding2.json' ...
INPUT_FILES_PATTERN = os.path.join(SCRIPT_DIR, 'qpoll_embedding*.json')

# [출력] Qdrant 업로드용 최종 파일
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'qpoll_upload_ready.json')

# --- 2. 헬퍼 함수 ---
def load_json(path):
    """JSON 파일을 로드합니다."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f) # [ {...}, {...}, ... ]
    except Exception as e:
        print(f"  > 파일 로드 오류: {os.path.basename(path)}, {e}")
        return None

# --- 3. 메인 실행 로직 ---
def main():
    # 모든 임베딩 객체를 저장할 마스터 리스트
    master_data = []
    
    # 1. 패턴에 맞는 모든 임베딩 파일 찾기
    embedding_files = glob.glob(INPUT_FILES_PATTERN)
    if not embedding_files:
        print(f"오류: '{INPUT_FILES_PATTERN}' 패턴에 맞는 임베딩 파일이 없습니다.")
        return

    print(f"--- 총 {len(embedding_files)}개의 임베딩 파일 병합 시작 ---")

    for file_path in embedding_files:
        print(f"  > 처리 중: {os.path.basename(file_path)}")
        data_list = load_json(file_path)
        
        if isinstance(data_list, list):
            
            # [수정] .extend() 대신 for 루프로 'topic_id' 제거
            count = 0
            for item in data_list:
                # 'topic_id' 키를 제거합니다. (키가 없어도 오류 없음)
                item.pop("topic_id", None) 
                master_data.append(item)
                count += 1
                
            print(f"    - {count}개 데이터 추가 완료 ('topic_id' 제외).")
        else:
            print(f"    - 건너뛰기: 파일 내용이 리스트 형식이 아닙니다.")

    # --- 최종 파일 저장 ---
    if not master_data:
        print("\n병합할 데이터가 없습니다.")
        return

    print(f"\n--- 최종 파일 저장 중 ---")
    try:
        # indent=4 제외 (파일 크기 절약)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False)
        
        print(f"성공! 총 {len(master_data)}개의 벡터가 '{OUTPUT_FILE}'에 저장되었습니다.")
        
    except Exception as e:
        print(f"최종 파일 저장 오류: {e}")

if __name__ == '__main__':
    main()