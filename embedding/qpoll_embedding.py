import os
import json
from sentence_transformers import SentenceTransformer # [수정] API 대신 라이브러리 import
from tqdm import tqdm # 진행률 표시
import numpy as np # [신규] 벡터를 리스트로 변환하기 위해 import

# --- 1. 경로 설정 ---
# 이 스크립트 파일(get_embeddings.py)의 위치
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # .../infra/embedding
# 상위 'infra' 폴더
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # .../infra

# [입력] master_qpoll_input.json 파일의 정확한 경로
INPUT_FILE = os.path.join(
    PROJECT_ROOT, 
    'embedding_preprocessing', 
    'merged_sentence_output_by_qpoll_topic',
    'merged_qpoll_text.json'
)

# [출력] 임베딩 결과는 이 스크립트와 동일한 폴더에 저장
OUTPUT_FILE = os.path.join(SCRIPT_DIR, 'qpoll_embeddings.json')

# [모델 설정]
# 사용할 Hugging Face 모델 ID
MODEL_ID = "nlpai-lab/KURE-v1"

# [성능 설정]
BATCH_SIZE = 64 # 한 번에 모델이 처리할 문장 수


# --- 2. 메인 실행 로직 ---

def main():
    print(f"입력 파일 로드 중: {INPUT_FILE}")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            master_data = json.load(f) # [ {panel_id: ..., sentence: ...}, ... ]
        if not master_data:
            print("오류: 파일에 데이터가 없습니다.")
            return
    except Exception as e:
        print(f"파일 로드 오류: {e}")
        return

    print(f"총 {len(master_data)}개의 문장을 임베딩합니다 (배치 크기: {BATCH_SIZE})...")

    # 1. [신규] 로컬에서 Sentence Transformer 모델 로드
    # (처음 실행 시 모델을 다운로드하므로 시간이 걸릴 수 있습니다)
    try:
        print(f"Hugging Face 모델 로드 중: {MODEL_ID}")
        # device='cuda'를 추가하면 GPU 사용 (GPU가 있는 경우)
        model = SentenceTransformer(MODEL_ID) 
        print("모델 로드 완료.")
    except Exception as e:
        print(f"모델 로드 실패: {e}")
        print("'pip install sentence-transformers torch'가 올바르게 설치되었는지 확인하세요.")
        return

    # 최종 임베딩 결과를 저장할 리스트
    embedded_data = []

    # 2. [수정] tqdm을 사용하여 배치 처리
    # (API 호출 대신 model.encode() 사용)
    for i in tqdm(range(0, len(master_data), BATCH_SIZE), desc="임베딩 진행 중"):
        
        batch = master_data[i : i + BATCH_SIZE]
        texts_to_embed = [item["sentence"] for item in batch]
        
        try:
            # 3. [핵심] 로컬에서 임베딩 수행 (API 호출 대체)
            # show_progress_bar=False (tqdm이 이미 외부 진행률 표시 중)
            vectors_batch = model.encode(texts_to_embed, show_progress_bar=False)
            
            # 4. [신규] 결과를 JSON 저장을 위해 numpy array -> python list로 변환
            vectors_batch_list = [v.tolist() for v in vectors_batch]
            
            # 5. 메타데이터와 벡터를 결합
            for idx, item in enumerate(batch):
                embedded_data.append({
                    "panel_id": item.get("panel_id"),
                    "topic_id": item.get("topic_id"),
                    "question": item.get("question"),
                    "sentence": item.get("sentence"),
                    "vector": vectors_batch_list[idx] # 로컬에서 생성된 벡터
                })
                
        except Exception as e:
            print(f"  > 배치 {i // BATCH_SIZE + 1} 임베딩 중 오류 발생: {e}")
            continue

    # --- 최종 파일 저장 ---
    if not embedded_data:
        print("\n임베딩된 데이터가 없습니다.")
        return

    print(f"\n--- 임베딩 완료. 총 {len(embedded_data)}개 벡터 파일 저장 중 ---")
    try:
        # indent=4 제외 (파일 크기 절약)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(embedded_data, f, ensure_ascii=False) 
        
        print(f"성공! 임베딩 결과가 '{OUTPUT_FILE}'에 저장되었습니다.")
        
    except Exception as e:
        print(f"최종 파일 저장 오류: {e}")

if __name__ == '__main__':
    main()