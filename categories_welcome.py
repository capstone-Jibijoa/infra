# -*- coding: utf-8 -*-
# categories_and_cleanse_welcome.py
#
# 이 스크립트는 'welcome_data.json'의 데이터를 정제하고 카테고리화하는 통합 프로세스입니다.
# 'cleanse_welcome.py'의 KNOWN_GOOD_MAP에 정의된 모든 컬럼에 대해 아래 로직을 적용합니다.
#
# 정제 로직 (각 컬럼에 대해 개별 적용):
# 1. KNOWN_GOOD_MAP에 정의된 기존 카테고리와 정확히 일치하는 데이터는 그대로 유지합니다.
# 2. 일치하지 않는 데이터는 Sentence Transformer 모델을 사용해 해당 컬럼의 기존 카테고리들과 의미적 유사도를 비교합니다.
#    - 유사도 점수가 임계값(SIMILARITY_THRESHOLD) 이상이면 가장 유사한 기존 카테고리로 매핑합니다.
# 3. 기존 카테고리로 매핑되지 않은 나머지 데이터는 BERTopic 모델을 사용해 새로운 클러스터(카테고리)로 그룹화합니다.
#
# --- 사용 전 준비사항 ---
# 1. 이 스크립트를 실행하기 전에 필요한 라이브러리를 설치해야 합니다.
#    터미널(명령 프롬프트)에 아래 명령어를 입력하여 설치하세요.
#
#    pip install pandas "scikit-learn<1.4.0" sentence-transformers bertopic
#
# 2. 이 스크립트는 'cleanse_welcome.py'와 같은 디렉토리에 위치해야 하며,
#    './xlsx_to_json_pipeline/welcome_data.json' 파일이 존재해야 합니다.

import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer, util
from bertopic import BERTopic

# 정제할 컬럼 목록 & 정상 값 목록 정의 (String 값이 들어 있는 컬럼만)
KNOWN_GOOD_MAP = {
    'job_title_raw': {
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
    },
    'job_duty_raw': {
        '경영•인사•총무•사무',
        '재무•회계•경리',
        '금융•보험•증권',
        '마케팅•광고•홍보•조사',
        '무역•영업•판매•매장관리',
        '고객상담•TM',
        '전문직•법률•인문사회•임원',
        '의료•간호•보건•복지',
        '교육•교사•강사•교직원',
        '방송•언론',
        '문화•스포츠',
        '서비스•여행•숙박•음식•미용•보안',
        '유통•물류•운송•운전',
        '디자인',
        '인터넷•통신',
        'IT',
        '모바일',
        '게임',
        '전자•기계•기술•화학•연구개발',
        '건설•건축•토목•환경',
        '생산•정비•기능•노무',
        np.nan
    },
    'phone_brand_raw': {
        '애플 (아이폰)',
        '삼성전자 (갤럭시, 노트)',
        'LG전자(V 시리즈, G 시리즈 등)',
        np.nan
    },
    'phone_model_raw': {
        '아이폰 15 Pro 시리즈',
        '아이폰 15 시리즈',
        '아이폰 14 Pro 시리즈',
        '아이폰 14 시리즈',
        '아이폰 13 Pro 시리즈',
        '아이폰 13/ 13mini',
        '아이폰 12 Pro 시리즈',
        '아이폰 12/ 12mini',
        '아이폰 11 Pro 시리즈',
        '아이폰 11',
        '아이폰 Xs/Xs Max',
        '아이폰 X',
        '아이폰 SE',
        '기타 아이폰 시리즈',
        '갤럭시 Z Fold 시리즈',
        '갤럭시 Z Filp 시리즈',
        '갤럭시 S23 시리즈',
        '갤럭시 S22 시리즈',
        '갤럭시 S21 시리즈',
        '갤럭시 S20 시리즈',
        '갤럭시 A 시리즈',
        '갤럭시 노트 시리즈',
        '갤럭시 M 시리즈',
        '기타 갤럭시 스마트폰',
        'LG 옵티머스 시리즈',
        'LG G Pro',
        'LG G Flex',
        'LG V 시리즈',
        'LG Q 시리즈',
        'LG X 시리즈',
        'LG 기타 스마트폰',
        np.nan
    },
    'car_manufacturer_raw': {
        '기아',
        '르노삼성',
        '쌍용',
        '쉐보레(한국GM/대우)',
        '현대',
        '제네시스',
        '아우디',
        '벤틀리',
        'BMW',
        '포드',
        '혼다',
        '인피니티',
        '재규어',
        '지프',
        '랜드로버',
        '렉서스',
        '링컨',
        '메르체데스-벤츠',
        'BMW미니',
        '닛산',
        '포르쉐',
        '롤스로이스',
        '테슬라',
        '토요타',
        '볼보',
        '폭스바겐',
        '만',
        '스카니아',
        '포톤',
        '이스트',
        '이베코',
        np.nan
    },
    'car_model_raw': {
        '레이', '모닝', 'K3', 'K5', 'K7', 'K8', '스팅어', 'K9', '카니발', '쏘울', '니로', '스토닉', '셀토스', '스포티지', '쏘렌토', '모하비', 'EV6', '봉고', '타이탄', '트레이드', '라이노', '복사', '그랜토', '세레스', '프론티어',
        '클리오', 'SM3', 'SM5', 'SM6', 'SM7', 'QM3', 'XM3', 'QM6', '야무진', 'SM510/530',
        '투리스모', '티볼리', '티볼리에어', '코란도(C300)', '코란도스포츠', 'G4렉스턴', '렉스턴스포츠', '렉스턴스포츠 칸', 'SY트럭',
        '스파크', '아베오', '볼트', '크루즈', '말리부', '임팔라', '카마로', '트랙스', '트레일블레이저', '트래버스', '콜로라도', '이쿼녹스', '라보', '노부스', '프리마', '바네트',
        '엑센트', 'i30', '아이오닉', '벨로스터', '아반떼', 'i40', '쏘나타', '그랜저', '코나', '투싼', '넥쏘', '싼타페', '스타렉스', '그랜드스타렉스', '팰리세이드', '베뉴', '포터', '마이티', '메가트럭', '메가와이드', '누파워트럭', '엑시언트', '슈퍼트럭', '트라고', '뉴파워트럭', '리베로',
        'G70', 'G80', 'G90', 'GV70', 'GV80',
        'A1', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'R8', 'TT',
        'Arnage (아나지)', 'Bentayga (번테이가)', 'Continental Flying Spur (컨티넨탈 플라잉 스퍼)', 'Continental GT (컨티넨탈 GT)', 'Continental GTC (컨티넨탈 GTC)', 'EXP 10', 'Mulsanne (뮬산)',
        '1-Series (1 시리즈)', '1-Series Sport Cross (1 시리즈 스포츠 크로스)', '2-Series (2 시리즈)', '2-Series Active Tourer (2 시리즈 액티브 투어러)', '2-Series Gran Coupe (2 시리즈 그랜 쿠페)',
        '3-Series (3 시리즈)', '3-Series GT (3 시리즈 GT)', '4-Series (4 시리즈)', '4-Series Gran Coupe (4 시리즈 그랜 쿠페)', '5-Series (5 시리즈)', '5-Series GT (5 시리즈 GT)',
        '6-Series (6 시리즈)', '6-Series Gran Coupe (6 시리즈 그랜 쿠페)', '7-Series (7 시리즈)', '9-Series (9 시리즈)', 'i3', 'i5', 'i8', 'X1', 'X3', 'X4', 'X5', 'X6', 'X7', 'Z3', 'Z4', 'Z8',
        'Escape (이스케이프)', 'Explorer (익스플로러)', 'Explorer Sport Trac (익스플로러 스포츠 트랙)', 'Focus (포커스)', 'Fusion (퓨전)', 'Kuga (쿠가)', 'Mondeo (몬데오)', 'Mustang (머스탱)', 'S-MAX', 'Taurus (토러스)', 'Taurus X (토러스 X)', 'Windstar (윈드스타)',
        'Accord (어코드)', 'Civic (시빅)', 'CrossTour (크로스투어)', 'CR-V', 'CR-Z', 'HR-V', 'Insight (인사이트)', 'Legend (레전드)', 'NSX', 'Odyssey (오딧세이)', 'Pilot (파일럿)', 'Vezel (베젤)',
        'EX', 'FX', 'G', 'G35', 'JX', 'M', 'Q11-15', 'Q50', 'Q60', 'Q70', 'QX', 'QX50', 'QX60', 'QX70', 'QX80',
        'E-PACE', 'F-PACE', 'F-Type', 'I-PACE', 'I-Type', 'S-Type', 'XE', 'XF', 'XJ', 'XK', 'X-Type',
        'Cherokee (체로키)', 'Commander (커맨더)', 'Compass (컴패스)', 'Grand Cherokee (그랜드 체로키)', 'Patriot (패트리어트)', 'Renegade (레니게이드)', 'Wrangler (랭글러)',
        'Defender Sport (디펜더 스포츠)', 'Discovery (디스커버리)', 'Discovery Sport (디스커버리 스포츠)', 'Freelander (프리랜더)', 'Range Rover (레인지로버)', 'Range Rover Evoque (레인지로버 이보크)',
        'Range Rover Grand Evoque(레인지로버 그랜드 이 보크)', 'Range Rover Sport (레인지로버 스포츠)',
        'CT', 'ES', 'GS', 'IS', 'LC', 'LS', 'NX', 'RC', 'RX', 'SC',
        'Aviator (에비에이터)', 'Continental (컨티넨탈)', 'MKC', 'MKS', 'MKX', 'MKZ', 'Town Car (타운카)', 'Nautilus (노틸러스)', 'Corsair (코세어)',
        'A-Class (A 클래스)', 'B-Class (B 클래스)', 'C-Class (C 클래스)', 'CL', 'CLA', 'CLE', 'CLK', 'CLS', 'Compact Sedan (컴팩트 세단)', 'E-Class (E 클래스)', 'G-Class (G 클래스)',
        'GLA', 'GLB', 'GLC', 'GLC Coupe (GLC 쿠페)', 'GLE', 'GLE Coupe (GLE 쿠페)', 'GLK', 'GLS', 'GT', 'GT-4', 'ML-Class (ML 클래스)', 'S-Class (S 클래스)', 'S-Class Coupe (S 클래스 쿠페)',
        'SL', 'SLC', 'SLK', 'SLS', 'EQC', '아테고', '악트로스', '아록스',
        'Clubman (클럽맨)', 'Countryman (컨트리맨)', 'Coupe (쿠페)', 'Mini (미니)', 'Paceman (페이스맨)', 'Roadster (로드스터)', 'Superleggera (슈퍼레제라)',
        '370Z', 'Altima (알티마)', 'Cube (큐브)', 'GT-R', 'Juke (쥬크)', 'Leaf (리프)', 'Maxima (맥시마)', 'Murano (무라노)', 'Pathfinder (패스파인더)', 'Qashqai (캐시카이)', 'Rogue (로그)',
        '911', '960', '718 Boxster (718 박스터)', '718 Cayman (718 카이맨)', '918 Spyder (918 스파이더)', 'Boxster (박스터)', 'Carrera GT (카레라 GT)', 'Cayenne (카이엔)', 'Cayenne Coupe (카이엔 쿠페)', 'Cayman (카이맨)', 'Macan (마칸)', 'Pajun (파준)', 'Panamera (파나메라)',
        'Dawn (던)', 'Ghost (고스트)', 'Phantom (팬텀)', 'Phantom Coupe (팬텀 쿠페)', 'Phantom Drophead Coupe(팬텀 드롭헤드 쿠페)', 'Wraith (레이스)',
        'Model 3 (모델 3)', 'Model S (모델 S)', 'Model X (모델 X)', 'Model Y (모델 Y)', '사이버트럭', '로드스터',
        'Avalon (아발론)', 'Camry (캠리)', 'Corolla (코롤라)', 'FJ Cruiser (FJ 크루저)', 'GT 86', 'Prius (프리우스)', 'Prius V (프리우스 V)', 'Prius C (프리우스 C)', 'RAV4', 'Sienna (시에나)', 'Tacoma (타코마)', 'Venza (벤자)', 'Alphard',
        'C30', 'C70', 'S40', 'S60', 'S80', 'S90', 'V40', 'V50', 'V60', 'V70', 'V90 Cross Country (V90 크로스 컨트리)', 'XC40', 'XC60', 'XC70', 'XC90', 'FL', 'FH', 'FMX',
        'Bora (보라)', 'CC', 'Eos', 'Golf (골프)', 'Jetta (제타)', 'New Beetle (뉴비틀)', 'New Beetle Convertible (뉴비틀 컨버터블)', 'Passat (파사트)', 'Phaeton (페이톤)', 'Polo (폴로)', 'Scirocco (시로코)', 'Tiguan (티구안)', 'Touareg (투아렉)', 'Touran (투란)', 'Arteon (아테온)',
        'TGM', 'TGS', 'TGX',
        'G', 'P', 'R', 'S',
        '아오마크', '엘프', '트래커',
        np.nan
    },
    'smoking_brand_etc_raw': {np.nan},
    'smoking_brand_other_details_raw': {np.nan},
    'drinking_experience_other_details_raw': {np.nan}
}

# 비교를 위한 공통 결측치/불필요 문자 정의
NULL_LIKE = ['', '없음', '모름', 'NA', 'N/A', '몰라요']

# --- 0. 설정 ---

# 입출력 파일 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(BASE_DIR, 'xlsx_to_json_pipeline', 'welcome_data.json')
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, 'welcome_data_cleansed_and_categorized.json')

# 의미 유사도 비교를 위한 임계값 (0.0 ~ 1.0 사이)
SIMILARITY_THRESHOLD = 0.75

# BERTopic 클러스터링을 위한 최소 그룹 크기
MIN_TOPIC_SIZE = 5

# 사용할 문장 임베딩 모델
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"


REPORT_FILE_PATH = os.path.join(BASE_DIR, 'categorization_report.txt')

def main():
    """
    데이터를 로드하고, KNOWN_GOOD_MAP에 정의된 모든 컬럼에 대해
    정제 및 카테고리화 작업을 수행한 후 결과와 보고서를 저장합니다.
    """
    print("--- 1. 데이터 로딩 ---")
    try:
        df = pd.read_json(INPUT_JSON_PATH, orient='records')
        print(f"성공적으로 '{INPUT_JSON_PATH}' 파일을 읽었습니다.")
    except FileNotFoundError:
        print(f"오류: 입력 파일('{INPUT_JSON_PATH}')을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"오류: JSON 파일을 읽는 중 예상치 못한 오류가 발생했습니다: {e}")
        return

    print(f"\n--- 2. 임베딩 모델({EMBEDDING_MODEL}) 로드 ---")
    print("모델 로드에는 몇 분 정도 소요될 수 있습니다...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("모델 로드 완료.")

    # 보고서 생성을 위한 데이터 수집용 딕셔너리
    report_data = {}

    # KNOWN_GOOD_MAP에 정의된 각 컬럼에 대해 정제 및 카테고리화 수행
    for col_raw in KNOWN_GOOD_MAP.keys():
        col_categorized = col_raw.replace('_raw', '_categorized')
        report_data[col_raw] = {}
        print(f"\n--- '{col_raw}' 컬럼 처리 시작 ---")

        if col_raw not in df.columns:
            print(f"경고: '{col_raw}' 컬럼이 데이터에 없어 건너뜁니다.")
            continue

        # 원본 데이터 복사 및 기본 정제
        df[col_categorized] = df[col_raw].astype(str).str.strip()
        df[col_categorized].replace(NULL_LIKE, np.nan, inplace=True)

        known_categories = [cat for cat in KNOWN_GOOD_MAP.get(col_raw, set()) if pd.notna(cat)]
        if not known_categories:
            print(f"'{col_raw}'에 대한 기존 카테고리가 없어 건너뜁니다.")
            continue

        exact_match_mask = df[col_categorized].isin(known_categories)
        to_be_cleansed_mask = ~exact_match_mask & df[col_categorized].notna()
        to_be_cleansed_items = df.loc[to_be_cleansed_mask, col_categorized].unique().tolist()

        print(f"총 {len(df)}개 중 {exact_match_mask.sum()}개는 기존 카테고리와 일치.")
        print(f"정제가 필요한 고유 항목 {len(to_be_cleansed_items)}개를 처리합니다.")

        # 보고서에 정확히 일치하는 항목 추가
        exact_matches = df.loc[exact_match_mask, [col_raw, col_categorized]].dropna()
        for _, row in exact_matches.iterrows():
            cat = row[col_categorized]
            raw_val = row[col_raw]
            if cat not in report_data[col_raw]:
                report_data[col_raw][cat] = set()
            report_data[col_raw][cat].add(raw_val)

        if not to_be_cleansed_items:
            print("새롭게 정제할 데이터가 없습니다.")
            continue

        category_embeddings = model.encode(known_categories, convert_to_tensor=True)
        item_embeddings = model.encode(to_be_cleansed_items, convert_to_tensor=True)
        cosine_scores = util.cos_sim(item_embeddings, category_embeddings)

        mapped_items = {}
        unmapped_items = []
        for i, item in enumerate(to_be_cleansed_items):
            best_match_score, best_match_idx = cosine_scores[i].max(dim=0)
            if best_match_score.item() >= SIMILARITY_THRESHOLD:
                mapped_category = known_categories[best_match_idx.item()]
                mapped_items[item] = mapped_category
                # 보고서 데이터 추가
                if mapped_category not in report_data[col_raw]:
                    report_data[col_raw][mapped_category] = set()
                report_data[col_raw][mapped_category].add(item)
            else:
                unmapped_items.append(item)
        
        print(f"의미 분석 결과: {len(mapped_items)}개 항목을 기존 카테고리로 매핑.")
        
        if mapped_items:
            df[col_categorized] = df[col_categorized].map(mapped_items).fillna(df[col_categorized])

        if not unmapped_items:
            print("신규 카테고리화 대상이 없습니다.")
        else:
            print(f"BERTopic으로 {len(unmapped_items)}개 항목 신규 카테고리화 시작...")
            actual_min_topic_size = min(MIN_TOPIC_SIZE, len(unmapped_items) // 2)
            if actual_min_topic_size < 2 : actual_min_topic_size = 2

            topic_model = BERTopic(embedding_model=model, min_topic_size=actual_min_topic_size, verbose=False)
            topics, _ = topic_model.fit_transform(unmapped_items)
            
            newly_categorized_items = {}
            for item, topic_id in zip(unmapped_items, topics):
                if topic_id == -1:
                    category_name = f'기타_{col_raw.replace("_raw","")}'
                    newly_categorized_items[item] = category_name
                else:
                    keywords = [word for word, _ in topic_model.get_topic(topic_id)]
                    category_name = f"신규_{col_raw.replace('_raw','')}_{topic_id}_{'_'.join(keywords[:2])}"
                    newly_categorized_items[item] = category_name
                
                # 보고서 데이터 추가
                if category_name not in report_data[col_raw]:
                    report_data[col_raw][category_name] = set()
                report_data[col_raw][category_name].add(item)

            df[col_categorized] = df[col_categorized].map(newly_categorized_items).fillna(df[col_categorized])
            print("신규 카테고리화 완료.")

    # --- 최종 결과 저장 ---
    save_results(df)
    save_report(report_data)

def save_results(df):
    """
    처리된 데이터프레임을 JSON 파일로 저장합니다.
    """
    try:
        new_order = []
        processed_cols = set()
        for col in df.columns:
            if '_categorized' in col:
                continue
            new_order.append(col)
            processed_cols.add(col)
            categorized_col = col.replace('_raw', '_categorized')
            if categorized_col in df.columns and categorized_col not in processed_cols:
                new_order.append(categorized_col)
                processed_cols.add(categorized_col)

        for col in df.columns:
            if col not in processed_cols:
                new_order.append(col)

        df_to_save = df[new_order]
        df_to_save.to_json(OUTPUT_JSON_PATH, orient='records', force_ascii=False, indent=4)
        print(f"\n--- 최종 결과를 '{OUTPUT_JSON_PATH}' 파일로 성공적으로 저장했습니다. ---")
    except Exception as e:
        print(f"\n오류: 최종 결과를 저장하는 중 예상치 못한 오류가 발생했습니다: {e}")

def save_report(report_data):
    """
    카테고리화 결과를 텍스트 파일 보고서로 저장합니다.
    """
    print(f"--- 카테고리화 보고서를 '{REPORT_FILE_PATH}' 파일로 저장합니다. ---")
    try:
        with open(REPORT_FILE_PATH, 'w', encoding='utf-8') as f:
            for col_raw, categories in report_data.items():
                f.write(f"--- '{col_raw}' 컬럼 카테고리화 보고서 ---\n\n")
                sorted_categories = sorted(categories.keys())
                for category in sorted_categories:
                    f.write(f"[ {category} ]\n")
                for category in sorted_categories:
                    f.write(f"[ {category} ]\n")
                    sorted_items = sorted(list(categories[category]))
                    for item in sorted_items:
                        f.write(f"  - {item}\n")
                    f.write("\n")
                f.write("\n")
        print("보고서 저장을 완료했습니다.")
    except Exception as e:
        print(f"\n오류: 보고서를 저장하는 중 예상치 못한 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    main()
