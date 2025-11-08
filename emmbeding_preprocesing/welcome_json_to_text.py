import os
import json
import re

# --- 1. 경로 설정 ---
# (경로 설정은 qpoll 스크립트와 동일한 구조를 가정합니다)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# welcome_data.json이 qpoll과 다른 폴더에 있을 수 있으니,
# 'xlsx_to_json_pipeline' 폴더를 직접 참조합니다.
INPUT_JSON_PATH = os.path.join(
    PROJECT_ROOT,
    'xlsx_to_json_pipeline',
    'welcome_data.json' # welcome_data.json은 qpoll_json_output 밖에 있었음
)

# Welcome 데이터용 문장 출력 폴더
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'sentence_output_by_welcome_category')


# --- 2. 카테고리 및 템플릿 정의 ---
#
# ⭐️ 사용자가 수정할 부분 ⭐️
#

# 2-1. 카테고리별로 'key' 목록을 정의합니다.
CATEGORIES = {
    "personal_info": [
        "gender", "birth_year", "region_major", "region_minor", 
        "marital_status", "children_count", "family_size", "education_level"
    ],
    "job_info": [
        "job_title_raw", "job_duty_raw", 
        "income_personal_monthly", "income_household_monthly"
    ],
    "electronics": [
        "owned_electronics"
    ],
    "phone": [
        "phone_brand_raw", "phone_model_raw"
    ],
    "car": [
        "car_ownership", "car_manufacturer_raw", "car_model_raw"
    ],
    "smoking": [
        "smoking_experience", "smoking_brand", "smoking_brand_etc_raw", 
        "e_cigarette_experience", "smoking_brand_other_details_raw"
    ],
    "drinking": [
        "drinking_experience", "drinking_experience_other_details_raw"
    ]
}

# 2-2. 카테고리별 맞춤형 문장 생성 함수를 정의합니다. (인자로 'panel' 객체를 받음)

def format_personal_info(panel):
    """[예시] 'personal_info' 카테고리를 하나의 문장으로 합성합니다."""
    
    # 패널 객체에서 값을 안전하게 가져옵니다.
    # (panel.get(key)는 값이 없으면 None을 반환합니다)
    gender = panel.get("gender")
    birth_year = panel.get("birth_year")
    region = panel.get("region_major") # 예시로 '주요' 지역만 사용
    marital = panel.get("marital_status")

    # 문장 조각들을 리스트에 담아 None이 아닌 것만 합칩니다.
    parts = []
    if gender:
        parts.append(f"성별은 {gender}")
    if birth_year:
        parts.append(f"{birth_year}년생")
    if region:
        parts.append(f"{region} 거주")
    if marital:
        parts.append(f"{marital} 상태")

    # 모든 정보가 비어있으면 None 반환
    if not parts:
        return None
        
    return ", ".join(parts) + "입니다."

def format_job_info(panel):
    """[예시] 'job_info' 카테고리를 하나의 문장으로 합성합니다."""
    job = panel.get("job_title_raw")
    income_h = panel.get("income_household_monthly")
    
    parts = []
    if job:
        parts.append(f"직업은 {job}")
    if income_h:
        parts.append(f"가구 소득은 {income_h}")
        
    if not parts:
        return None
    
    return ", ".join(parts) + "입니다."

def format_default_category(panel, key_list):
    """
    [기본 템플릿] 맞춤 함수가 없는 카테고리는 이 함수를 사용합니다.
    (예: "car" 카테고리)
    """
    parts = []
    for key in key_list:
        value = panel.get(key)
        
        # 값이 없으면(None) 건너뜀
        if value is None:
            continue
            
        # 값이 리스트인 경우 (예: owned_electronics)
        if isinstance(value, list):
            if not value: continue # 빈 리스트 건너뜀
            # "기타", "없음" 등 필터링
            filtered = [str(v) for v in value if v not in ["기타", "없음"]]
            if filtered:
                parts.append(f"{key}: {', '.join(filtered)}")
        
        # 값이 리스트가 아닌 경우
        else:
            value_str = str(value)
            if value_str not in ["기타", "없음"]:
                parts.append(f"{key}: {value_str}")

    if not parts:
        return None
        
    return ". ".join(parts) + "."


# 2-3. '카테고리 이름'과 '사용할 함수'를 매핑합니다.
# ⭐️ 여기에 등록되지 않은 카테고리는 'format_default_category'를 사용합니다.
CATEGORY_FORMATTERS = {
    "personal_info": format_personal_info,
    "job_info": format_job_info,
    # "electronics": format_my_electronics_func, # (필요시 맞춤 함수 추가)
}


# --- 3. 헬퍼 함수 ---

def load_data(path):
    """통합 JSON 파일을 로드합니다."""
    print(f"원본 데이터 로드 중... (경로: {path})")
    if not os.path.exists(path):
        print(f"오류: 입력 파일 '{path}'을(를) 찾을 수 없습니다.")
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f) # [ {panel_id: A, ...}, {panel_id: B, ...} ]
        print(f"성공: 총 {len(data)}명의 패널 데이터를 로드했습니다.")
        return data
    except Exception as e:
        print(f"JSON 로드 오류: {e}")
        return None

def clean_filename(text):
    """키 이름을 안전한 파일명으로 변환합니다."""
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    return text.strip()[:50]

# --- 4. 메인 실행 로직 ---

def main():
    # 1. 출력 폴더 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 2. 데이터 로드 (패널 리스트)
    panel_data = load_data(INPUT_JSON_PATH)
    if not isinstance(panel_data, list):
        print("오류: 입력 데이터가 리스트 형식이 아닙니다.")
        return

    # 3. [신규] '카테고리'별로 순회하며 파일 생성
    print("\n--- 카테고리별 문장 생성 및 파일 저장 시작 ---")
    
    file_count = 0
    # (예: category_name = "personal_info", key_list = ["gender", "birth_year", ...])
    for category_name, key_list in CATEGORIES.items():
        
        print(f"  > 처리 중: {category_name}")
        
        # 4. 이 카테고리에 맞는 포맷터(함수)를 가져옴
        # (맵에 없으면 format_default_category를 사용)
        formatter = CATEGORY_FORMATTERS.get(category_name)
        
        generated_data = [] # 이 카테고리의 결과물 리스트
        
        # 5. '모든 패널'을 순회
        for panel in panel_data:
            if not isinstance(panel, dict): continue

            panel_id = panel.get('panel_id')
            if not panel_id: continue

            # 6. 문장 생성
            if formatter:
                # 6-A. 맞춤형 함수가 등록된 경우 (예: personal_info)
                sentence = formatter(panel)
            else:
                # 6-B. 맞춤형 함수가 없는 경우 (예: car, phone)
                sentence = format_default_category(panel, key_list)
            
            generated_data.append({
                "panel_id": panel_id,
                "sentence_for_embedding": sentence
                # "category": category_name # (메타데이터가 필요하면 추가)
            })

        # 7. 이 '카테고리'에 대한 최종 출력 객체 생성
        output_data = {
            "topic_category": category_name,
            "generated_data": generated_data
        }

        # 8. 파일명 생성 (예: personal_info.json)
        safe_name = clean_filename(category_name)
        filename = f"{safe_name}.json"
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            file_count += 1
        except Exception as e:
            print(f"  > 파일 저장 오류 ({filename}): {e}")

    print(f"\n--- 작업 완료 ---")
    print(f"총 {file_count}개의 카테고리 파일을 '{OUTPUT_DIR}' 폴더에 저장했습니다.")

if __name__ == '__main__':
    main()