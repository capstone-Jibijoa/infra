import pandas as pd
import numpy as np
import json
import re
import os

# --- 0. 설정 ---

# 입력/출력 경로 설정
# __file__은 현재 스크립트의 경로를 나타냅니다.
# os.path.dirname()으로 스크립트가 있는 디렉토리를 구합니다.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_JSON_PATH = os.path.join(BASE_DIR, 'xlsx_to_json_pipeline', 'welcome_data.json')
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, 'welcome_data_cleansed.json')


# 정제할 컬럼 목록
RAW_COLUMNS = [
    'job_title_raw',
    'job_duty_raw',
    'phone_brand_raw',
    'phone_model_raw',
    'car_manufacturer_raw',
    'car_model_raw',
    'smoking_brand_etc_raw',
    'smoking_brand_other_details_raw',
    'drinking_experience_other_details_raw'
]

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

# A. 범주화 함수(직업/직무용)
def clean_job_category(series):
    """ '회사원' 등이 제외된 '대기업 인사팀', '개발자' 등에 적용 """
    # np.select가 가장 효율적입니다.
    conditions = [
        series.str.contains(r'개발|코딩|IT|SW|프로그래머', na=False, case=False),
        series.str.contains(r'사무|경리|인사|회계|총무', na=False, case=False),
        series.str.contains(r'영업|마케팅|기획|MD', na=False, case=False),
        series.str.contains(r'교사|강사|교육', na=False, case=False)
    ]
    choices = [
        'IT/개발직',
        '사무/행정직',
        '영업/마케팅직',
        '교육직'
    ]
    # 매핑되지 않는 값은 '기타_주관식' 또는 원본(series) 반환
    return np.select(conditions, choices, default='기타_주관식')

# B. 표준화/추출 함수 (브랜드/모델용)
def clean_phone_model(series):
    """ '갤럭시 S24 울트라', 'iPhone 15 pro max' 등에 적용 """

    def extract_model(x):
        if pd.isna(x): return np.nan
        x_lower = str(x).lower()

        # 아이폰 시리즈 추출
        if 'iphone' in x_lower or '아이폰' in x_lower:
            match = re.search(r'(iphone|아이폰)\s*(\d{1,2})', x_lower)
            if match: return f'iPhone {match.group(2)} Series'

        # 갤럭시 S/Z 시리즈 추출
        if 'galaxy' in x_lower or '갤럭시' in x_lower:
            match = re.search(r'(galaxy|갤럭시)\s*([sz])\s*(\d{1,2})', x_lower)
            if match: return f'Galaxy {match.group(2).upper()}{match.group(3)}'

        return '기타_모델' # 또는 원본(x) 반환

    return series.apply(extract_model)

def clean_car_maker(series):
    """ '현대', '기아' 등이 제외된 '횬대', 'Hundae' 등에 적용 """
    # 간단한 오탈자 교정
    replace_map = {
        r'.*현대.*|.*hundae.*|.*hyundai.*': '현대',
        r'.*기아.*|.*kya.*': '기아',
        r'.*삼성.*|.*르노.*': '르노삼성'
    }
    return series.replace(replace_map, regex=True)

# C. 키워드 추출/제거 함수 (기타 상세용)
def clean_drinking_details(series):
    """ '친구들과 마심', '소주 한병' 등에 적용 """
    def categorize(s):
        if pd.isna(s):
            return np.nan
        s_lower = str(s).lower()
        if any(keyword in s_lower for keyword in ['소주', '맥주', '와인', '위스키', '막걸리']):
            return '주류_언급'
        if any(keyword in s_lower for keyword in ['안마심', '금주']):
            return '금주_언급'
        return np.nan

    return series.apply(categorize)

def main():
    """데이터를 읽어 정제하고 저장하는 메인 함수"""
    print("데이터 정제를 시작합니다...")

    try:
        df = pd.read_json(INPUT_JSON_PATH, orient='records')
        print(f"성공적으로 {INPUT_JSON_PATH} 파일을 읽었습니다.")
    except FileNotFoundError:
        print(f"오류: 입력 파일({INPUT_JSON_PATH})을 찾을 수 없습니다.")
        return
    except Exception as e:
        print(f"오류: JSON 파일을 읽는 중 예상치 못한 오류가 발생했습니다: {e}")
        return

    for col in RAW_COLUMNS:
        if col not in df.columns:
            print(f"경고: '{col}' 컬럼이 파일에 존재하지 않아 건너뜁니다.")
            continue

        # 1. 양쪽 공백 제거 및 타입 변환
        df[col] = df[col].astype(str).str.strip()

        # 2. 공통 결측치를 np.nan으로 표준화
        df[col].replace(NULL_LIKE, np.nan, inplace=True)

        # 3. 새 컬럼명 생성 (예: 'job_title_clean')
        new_col = col.replace('_raw', '_clean')

        # 4. 해당 컬럼의 '정상값' 목록 가져오기
        known_list = KNOWN_GOOD_MAP.get(col, {np.nan})

        # 5. [핵심] 정제 대상 마스크 생성
        mask = ~df[col].isin(known_list) & df[col].notna()

        # 6. 새 컬럼을 원본 값으로 우선 초기화
        df[new_col] = df[col]

        # 7. 정제 대상 데이터(주관식 값) 추출
        to_clean_series = df.loc[mask, new_col]

        if to_clean_series.empty:
            print(f"[{col}] 정제 대상 없음. (Skipped)")
            continue

        print(f"[{col}] -> [{new_col}] : {len(to_clean_series)} 건 정제 중...")

        # 8. 컬럼별로 정의된 정제 함수 적용
        if col in ['job_title_raw', 'job_duty_raw']:
            cleaned_values = clean_job_category(to_clean_series)
            df.loc[mask, new_col] = cleaned_values

        elif col == 'car_manufacturer_raw':
            cleaned_values = clean_car_maker(to_clean_series)
            df.loc[mask, new_col] = cleaned_values

        elif col == 'phone_model_raw': # car_model_raw도 유사하게 적용 가능
            cleaned_values = clean_phone_model(to_clean_series)
            df.loc[mask, new_col] = cleaned_values

        elif col == 'drinking_experience_other_details_raw':
            cleaned_values = clean_drinking_details(to_clean_series)
            df.loc[mask, new_col] = cleaned_values

        elif col in ['smoking_brand_etc_raw', 'smoking_brand_other_details_raw', 'car_model_raw']:
            # car_model_raw는 현재 별도 정제 함수가 없으므로, 기타 항목처럼 nan 처리
            # 추후 car_model_raw에 대한 정제 함수를 추가할 수 있습니다.
            df.loc[mask, new_col] = np.nan
        
        else:
            # 정의되지 않은 다른 컬럼들은 일단 nan 처리
            df.loc[mask, new_col] = np.nan


    try:
        df.to_json(OUTPUT_JSON_PATH, orient='records', force_ascii=False, indent=4)
        print(f"\n정제된 데이터를 {OUTPUT_JSON_PATH} 파일로 성공적으로 저장했습니다.")
    except Exception as e:
        print(f"\n오류: 정제된 데이터를 저장하는 중 예상치 못한 오류가 발생했습니다: {e}")


if __name__ == '__main__':
    main()