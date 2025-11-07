# -*- coding: utf-8 -*-
# discover_categories.py
#
# 이 스크립트는 'welcome_data.json' 파일에서 직업(job_title_raw) 데이터를 읽어,
# BERTopic 라이브러리를 사용해 의미적으로 유사한 직업끼리 자동으로 그룹화(클러스터링)합니다.
# 이를 통해 데이터에 숨어있는 직업 카테고리를 발견할 수 있습니다.
#
# --- 사용 전 준비사항 ---
# 1. 이 스크립트를 실행하기 전에 필요한 라이브러리를 설치해야 합니다.
#    터미널(명령 프롬프트)에 아래 명령어를 입력하여 설치하세요.
#
#    pip install bertopic "scikit-learn<1.4.0"
#
# 2. 이 스크립트는 'cleanse_welcome.py'와 같은 디렉토리에 위치해야 하며,
#    './xlsx_to_json_pipeline/welcome_data.json' 파일이 존재해야 합니다.

import pandas as pd
import numpy as np
import os
from bertopic import BERTopic

# --- 0. 설정 ---

# 입력 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(BASE_DIR, 'xlsx_to_json_pipeline', 'welcome_data.json')

# 'cleanse_welcome.py'에서 사용하는 상수들을 가져와 정제 대상을 동일하게 식별합니다.
# 미리 정의된 정상 값 목록
KNOWN_GOOD_JOB_TITLES = {
    '전문직 (의사, 간호사, 변호사, 회계사, 예술가, 종교인, 엔지니어, 프로그래머, 기술사 등)',
    '교직 (교수, 교사, 강사 등)',
    '경영/관리직 (사장, 대기업 간부, 고위 공무원 등)',
    '사무직 (기업체 차장 이하 사무직 종사자, 공무원 등)',
    '자영업 (제조업, 건설업, 도소매업, 운수업, 무역업, 서비스업 경영)',
    '판매직 (보험판매, 세일즈맨, 도/소매업 직원, 부동산 판매, 행상, 노점상 등)',
    '서비스직 (미용, 통신, 안내, 요식업 직원 등)',
    '생산/노무직 (차량운전자, 현장직, 생산직 등)',
    '기능직 (기술직, 제빵업, 목수, 전기공, 정비사, 배관공 등)',
    '농업/임업/축산업/광업/수산업',
    '임대업',
    '중/고등학생',
    '대학생/대학원생',
    '전업주부',
    '퇴직/연금생활자',
    np.nan
}
# 공통 결측치/불필요 문자
NULL_LIKE = ['', '없음', '모름', 'NA', 'N/A', '몰라요']


def discover_job_categories():
    """
    JSON 파일에서 직업 데이터를 읽어 BERTopic으로 클러스터링하고 결과를 출력합니다.
    """
    print("--- 데이터 로딩 및 전처리 시작 ---")
    # --- 1. 데이터 로딩 ---
    try:
        df = pd.read_json(INPUT_JSON_PATH, orient='records')
        print(f"성공적으로 '{INPUT_JSON_PATH}' 파일을 읽었습니다.")
    except FileNotFoundError:
        print(f"오류: 입력 파일('{INPUT_JSON_PATH}')을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"오류: JSON 파일을 읽는 중 예상치 못한 오류가 발생했습니다: {e}")
        return

    # --- 2. 분석 대상 데이터 추출 ---
    # 'job_title_raw' 컬럼이 없는 경우 처리
    if 'job_title_raw' not in df.columns:
        print("오류: 'job_title_raw' 컬럼을 찾을 수 없습니다.")
        return

    # 공백 제거 및 결측치 표준화
    job_titles = df['job_title_raw'].astype(str).str.strip()
    job_titles.replace(NULL_LIKE, np.nan, inplace=True)

    # 미리 정의된 값과 결측치를 제외한, 실제 사용자가 입력한 '주관식' 직업명만 추출
    mask = ~job_titles.isin(KNOWN_GOOD_JOB_TITLES) & job_titles.notna()
    unique_jobs = job_titles[mask].unique().tolist()

    if not unique_jobs:
        print("분석할 주관식 직업 데이터가 없습니다.")
        return

    print(f"총 {len(df)}개의 데이터에서 {len(unique_jobs)}개의 고유한 주관식 직업명을 발견했습니다.")
    print("--- 데이터 로딩 및 전처리 완료 ---")

    # --- 3. BERTopic 모델로 클러스터링 수행 ---
    print("--- BERTopic 모델 로딩 및 클러스터링 시작 ---")
    print("모델을 다운로드하고 학습하는 데 몇 분 정도 소요될 수 있습니다...")

    # 한국어 문장 임베딩 모델을 사용하여 BERTopic 인스턴스 생성
    # "jhgan/ko-sroberta-multitask"는 한국어 문장 이해에 성능이 좋은 모델 중 하나입니다.
    # min_topic_size: 토픽(그룹)으로 인정받기 위한 최소 항목 수. 이 값을 조절하여 그룹의 크기를 제어할 수 있습니다.
    topic_model = BERTopic(embedding_model="jhgan/ko-sroberta-multitask", min_topic_size=10, verbose=True)

    # 직업명 목록으로 모델 학습 및 토픽 예측
    topics, _ = topic_model.fit_transform(unique_jobs)

    print("--- 클러스터링 완료 ---")

    # --- 4. 결과 파일에 저장 ---
    OUTPUT_FILE_PATH = os.path.join(BASE_DIR, 'discovered_categories.txt')
    print(f"--- 클러스터링 결과를 '{OUTPUT_FILE_PATH}' 파일에 저장합니다. ---")

    try:
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("--- 클러스터링 결과 ---\n")
            # 생성된 토픽(그룹)의 개요를 문자열로 변환하여 파일에 쓰기
            f.write(topic_model.get_topic_info().to_string())
            f.write("\n\n")

            f.write("--- 각 그룹별 상세 내용 ---\n")
            # 각 그룹(토픽)에 속한 직업명들을 파일에 쓰기
            # -1번 토픽은 어떤 그룹에도 속하지 못한 '아웃라이어'들입니다.
            for topic_id in sorted(topic_model.get_topics().keys()):
                topic_keywords = [word for word, _ in topic_model.get_topic(topic_id)]
                documents_in_topic = [doc for doc, doc_topic_id in zip(unique_jobs, topics) if doc_topic_id == topic_id]
                
                f.write(f"\n[ 그룹 #{topic_id} | 주요 키워드: {', '.join(topic_keywords[:5])} ]\n")
                f.write(f"  (총 {len(documents_in_topic)}개 항목)\n")
                # 각 그룹별로 최대 10개 항목만 샘플로 파일에 쓰기
                f.write(f"  샘플 항목: {documents_in_topic[:10]}\n")
        
        print(f"성공적으로 결과를 '{OUTPUT_FILE_PATH}'에 저장했습니다.")

    except IOError as e:
        print(f"오류: 파일('{OUTPUT_FILE_PATH}')을 쓰는 중 I/O 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"오류: 결과를 파일에 저장하는 중 예상치 못한 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    discover_job_categories()
