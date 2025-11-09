import psycopg2
from psycopg2 import extras
import pandas as pd
import json
import logging
from tqdm import tqdm
from datetime import datetime
import math
import typing as t
import argparse

from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_core.documents import Document
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings

# -------------------- 설정 --------------------
DB_CONFIG = {
    "host": "project-main-db.crkcc42287ai.ap-southeast-2.rds.amazonaws.com",
    "dbname": "project_db",
    "user": "infra_master",
    "password": "precap111",
    "port": 5432
}

EMBEDDING_MODEL_NAME = "nlpai-lab/KURE-v1"
VECTOR_SIZE = 1024
QDRANT_HOST = "52.63.128.220"
QDRANT_PORT = 6333
COLLECTION_NAME = "welcome_subjective_vectors"
BATCH_SIZE = 50

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# -------------------- 유틸리티 --------------------
def clean_data_val(value: t.Any) -> t.Any:
    if value is None: return None
    if isinstance(value, float) and math.isnan(value): return None
    if isinstance(value, str) and value.strip() in ['NaN', 'nan', '']: return None
    if isinstance(value, list) and not value: return None
    return value


# -------------------- 텍스트 빌더 --------------------
def build_demo_basic_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    parts = []
    gender, birth = clean_data_val(d.get("gender")), clean_data_val(d.get("birth_year"))
    gender_str = {'F': '여성', 'M': '남성'}.get(gender)
    if gender_str and birth:
        try: age_group = f"{(datetime.now().year - int(birth)) // 10 * 10}대"
        except: age_group = ""
        parts.append(f"성별은 {gender_str}이고, 연령대는 {age_group}입니다.")
    region_info = next((r for r in [clean_data_val(d.get("region_major")), clean_data_val(d.get("region_minor")), clean_data_val(d.get("Q12_2"))] if r), None)
    if region_info: parts.append(f"거주지는 {region_info} 지역입니다.")
    return " ".join(parts) if parts else None


def build_family_status_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    parts = []
    marital, family = clean_data_val(d.get("marital_status")), clean_data_val(d.get("family_size"))
    children_count = clean_data_val(d.get("children_count"))

    if children_count is not None:
        try:
            if isinstance(children_count, (float, str)):
                children_count = int(float(children_count))
        except ValueError:
            pass

    if marital and family: parts.append(f"현재 {marital} 상태이며, 가족 구성원은 {family}입니다.")
    if children_count is not None: parts.append(f"자녀는 {children_count}명 있습니다.")
    return " ".join(parts) if parts else None


def build_job_education_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    parts = []
    job_title, duty = clean_data_val(d.get("job_title_raw")), clean_data_val(d.get("job_duty_raw"))
    edu = clean_data_val(d.get("education_level"))
    if job_title: parts.append(f"직업은 {job_title}이고" + (f", 직무는 {duty}에 종사합니다." if duty else ""))
    if edu: parts.append(f"최종학력은 {edu}입니다.")
    return " ".join(parts) if parts else None


def build_income_level_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    income_personal = clean_data_val(d.get("income_personal_monthly"))
    income_house = clean_data_val(d.get("income_household_monthly"))
    if income_personal and income_house:
        return f"소득 수준은 개인 월소득 {income_personal}, 가구 월소득 {income_house}입니다."
    return None


def build_tech_owner_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    electronics = clean_data_val(d.get("owned_electronics"))
    if electronics:
        top_items = ', '.join(electronics[:30])
        return f"전자제품은 {top_items} 등 총 {len(electronics)}종 보유 중입니다."
    return None


def build_car_owner_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    car_ownership = clean_data_val(d.get("car_ownership"))
    car_manufacturer = clean_data_val(d.get("car_manufacturer_raw"))
    car_model = clean_data_val(d.get("car_model_raw"))
    if car_ownership == "있다":
        info = "차량을 소유하고 있습니다."
        if car_manufacturer and car_model: info += f" 차량 모델은 '{car_manufacturer} {car_model}'입니다."
        elif car_manufacturer: info += f" 선호 브랜드는 '{car_manufacturer}'입니다."
        return info
    elif car_ownership == "없다":
        return "차량을 소유하고 있지 않습니다."
    return None


def build_drink_habit_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    drink_exp = clean_data_val(d.get("drinking_experience"))
    if drink_exp and '최근 1년 이내 술을 마시지 않음' not in drink_exp:
        types = ', '.join(drink_exp[:3])
        other = clean_data_val(d.get("drinking_experience_other_details_raw"))
        info = f"음주는 {types} 등 경험하였습니다."
        if other: info += f", 기타: {other}"
        return info
    return None


def build_smoke_habit_text(d: t.Dict[str, t.Any]) -> t.Optional[str]:
    smoke_exp = clean_data_val(d.get("smoking_experience"))
    if smoke_exp and '담배를 피워본 적이 없다' not in smoke_exp:
        smoke_brand = clean_data_val(d.get("smoking_brand"))
        e_cigarette = clean_data_val(d.get("e_cigarette_experience"))
        info = "흡연 경험이 있고,"
        if smoke_brand: info += f" 선호 브랜드는 {', '.join(smoke_brand[:2])}입니다."
        if e_cigarette: info += f" 전자담배 경험은 {', '.join(e_cigarette[:2])}입니다."
        return info
    return None


# -------------------- DB 로드 함수 --------------------
def load_welcome_meta(start_pid: int, end_pid: int):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    cur.execute(f"""
        SELECT pid, panel_id, structured_data, created_at
        FROM welcome_meta2
        WHERE pid BETWEEN {start_pid} AND {end_pid}
        ORDER BY pid;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# -------------------- 메인 함수 --------------------
def generate_subjective_qdrant(start_pid: int, end_pid: int):
    logging.info(f"PID {start_pid} ~ {end_pid} 구간 데이터 처리 시작")

    rows = load_welcome_meta(start_pid, end_pid)
    logging.info(f"총 {len(rows)}명 데이터 불러옴")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    raw_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT, timeout=300)
    qdrant_store = Qdrant(client=raw_client, collection_name=COLLECTION_NAME, embeddings=embeddings)

    # ✅ 컬렉션 초기화는 첫 번째 담당자만 수행
    if start_pid == 1:
        raw_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
        )
        logging.info(f"Qdrant 컬렉션 '{COLLECTION_NAME}' 초기화 완료")

    documents_to_add = []

    for row in tqdm(rows):
        pid = row["pid"]
        panel_id = row["panel_id"]
        structured_data = row["structured_data"]

        if not isinstance(structured_data, dict):
            try:
                structured_data = json.loads(structured_data)
            except Exception as e:
                logging.warning(f"{pid} structured_data JSON 변환 실패: {e}")
                continue

        for chunk_type, builder in [
            ("DEMO_BASIC", build_demo_basic_text),
            ("FAMILY_STATUS", build_family_status_text),
            ("JOB_EDUCATION", build_job_education_text),
            ("INCOME_LEVEL", build_income_level_text),
            ("TECH_OWNER", build_tech_owner_text),
            ("CAR_OWNER", build_car_owner_text),
            ("DRINK_HABIT", build_drink_habit_text),
            ("SMOKE_HABIT", build_smoke_habit_text)
        ]:
            text = builder(structured_data)
            if text:
                doc = Document(
                    page_content=text,
                    metadata={
                        "panel_id": panel_id,
                        "category": chunk_type
                    }
                )
                documents_to_add.append(doc)

        if len(documents_to_add) >= BATCH_SIZE:
            qdrant_store.add_documents(documents_to_add)
            documents_to_add.clear()

    if documents_to_add:
        qdrant_store.add_documents(documents_to_add)

    logging.info(f"✅ PID {start_pid}~{end_pid} 데이터 Qdrant 적재 완료")


# -------------------- 실행 --------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True, help="시작 pid")
    parser.add_argument("--end", type=int, required=True, help="끝 pid")
    args = parser.parse_args()

    generate_subjective_qdrant(args.start, args.end)
